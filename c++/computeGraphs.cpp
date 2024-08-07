void
STKDiscretization::computeGraphs()
{
  TEUCHOS_FUNC_TIME_MONITOR("STKDiscretization: computeGraphs");
  const auto vs = getVectorSpace();
  const auto ov_vs = getOverlapVectorSpace();
  m_jac_factory = Teuchos::rcp(new ThyraCrsMatrixFactory(vs, vs, ov_vs, ov_vs));

  // Determine which equations are defined on the whole domain,
  // as well as what eqn are on each sideset
  std::vector<int> volumeEqns;
  std::map<std::string,std::vector<int>> ss_to_eqns;
  for (int k=0; k < neq; ++k) {
    if (sideSetEquations.find(k) == sideSetEquations.end()) {
      volumeEqns.push_back(k);
    }
  }
  const int numVolumeEqns = volumeEqns.size();

  // The global solution dof manager
  const auto sol_dof_mgr = getDOFManager();
  const int num_elems = sol_dof_mgr->cell_indexer()->getNumLocalElements();

  // Handle the simple case, and return immediately
  if (numVolumeEqns==neq) {
    // This is the easy case: couple everything with everything
    for (int icell=0; icell<num_elems; ++icell) {
      const auto& elem_gids = sol_dof_mgr->getElementGIDs(icell);
      m_jac_factory->insertGlobalIndices(elem_gids,elem_gids,true);
    }
    m_jac_factory->fillComplete();
    return;
  }

  // Ok, if we're here there is at least 1 side equation
  Teuchos::Array<GO> rows,cols;

  // First, couple global eqn (row) coupled with global eqn (col)
  for (int icell=0; icell<num_elems; ++icell) {
    const auto& elem_gids = sol_dof_mgr->getElementGIDs(icell);

    for (int ieq=0; ieq<numVolumeEqns; ++ieq) {

      // Couple eqn=ieq with itself
      const auto& row_gids_offsets = sol_dof_mgr->getGIDFieldOffsets(volumeEqns[ieq]);
      const int num_row_gids = row_gids_offsets.size();
      rows.resize(num_row_gids);
      for (int idof=0; idof<num_row_gids; ++idof) {
        rows[idof] = elem_gids[row_gids_offsets[idof]];
      }
      m_jac_factory->insertGlobalIndices(rows(),rows(),false);

      // Couple eqn=ieq with eqn=jeq!=ieq
      for (int jeq=0; jeq<numVolumeEqns; ++jeq) {
        const auto& col_gids_offsets = sol_dof_mgr->getGIDFieldOffsets(jeq);
        const int num_col_gids = col_gids_offsets.size();
        cols.resize(num_col_gids);
        for (int jdof=0; jdof<num_col_gids; ++jdof) {
          cols[jdof] = elem_gids[col_gids_offsets[jdof]];
        }
        m_jac_factory->insertGlobalIndices(rows(),cols(),true);
      }
    }

    // While at it, for side set equations, set the diag entry, so that jac pattern
    // is for sure non-singular in the volume.
    for (const auto& it : sideSetEquations) {
      int eq = it.first;
      const auto& eq_offsets = sol_dof_mgr->getGIDFieldOffsets(eq);
      for (auto o : eq_offsets) {
        GO row = elem_gids[o];
        m_jac_factory->insertGlobalIndices(row,row,false);
      }
    }
  }

  // Now, process rows/cols corresponding to ss equations
  const auto& cell_layers_data_lid = stkMeshStruct->local_cell_layers_data;
  const auto& cell_layers_data_gid = stkMeshStruct->global_cell_layers_data;
  const auto SIDE_RANK = metaData->side_rank();
  for (const auto& it : sideSetEquations) {
    const int side_eq = it.first;

    // If the side eqn is column-coupled, it needs special treatment.
    // A side eqn can be coupled to the whole column if
    //   1) the mesh is layered, AND
    //   2) all sidesets where it's defined are on the top or bottom
    int allowColumnCoupling = not cell_layers_data_lid.is_null();
    if (not cell_layers_data_lid.is_null()) {
      for (const auto& ss_name : it.second) {
        std::vector<stk::mesh::Entity> sides;
        stk::mesh::Selector sel (*stkMeshStruct->ssPartVec.at(ss_name));
        stk::mesh::get_selected_entities(sel,bulkData()->buckets(SIDE_RANK),sides);
        if (sides.size()==0) {
          // This rank owns 0 sides on this sideset
          continue;
        }

        // Grab any side of this side set and check layerId and pos within element
        const auto& s = sides[0];
        const auto& e = bulkData->begin_elements(s)[0];
        const auto pos = determine_entity_pos(e,s);
        const auto layer = cell_layers_data_gid->getLayerId(stk_gid(e));

        if (layer==(cell_layers_data_lid->numLayers-1)) {
          allowColumnCoupling = pos==cell_layers_data_lid->top_side_pos;
        } else if (layer==0) {
          allowColumnCoupling = pos==cell_layers_data_lid->bot_side_pos;
        } else {
          // The mesh is layered, but this sideset is niether top nor bottom
          allowColumnCoupling = false;
        }
      }
    }
    // NOTE: Teuchos::reduceAll does not accept bool Packet, despite offerint REDUCE_AND as reduction op, so use int
    int globalAllowColumnCoupling = allowColumnCoupling;
    Teuchos::reduceAll(*comm(),Teuchos::REDUCE_AND,1,&allowColumnCoupling,&globalAllowColumnCoupling);

    // Loop over all side sets where this eqn is defined
    for (const auto& ss_name : it.second) {
      for (int ws=0; ws<getNumWorksets(); ++ws) {
        const auto& elem_lids = getElementLIDs_host(ws);
        const auto& ss = sideSets[ws].at(ss_name);

        // Loop over all sides in this side set
        for (const auto& side : ss) {
          const LO ws_elem_idx = side.ws_elem_idx;
          const LO elem_LID = elem_lids(ws_elem_idx);
          const auto& side_elem_gids = sol_dof_mgr->getElementGIDs(elem_LID);
          const int side_pos = side.side_pos;
          const auto& side_eq_offsets = sol_dof_mgr->getGIDFieldOffsetsSide(side_eq,side_pos);

          // Compute row GIDs
          const int num_row_gids = side_eq_offsets.size();
          rows.resize(num_row_gids);
          for (int idof=0; idof<num_row_gids; ++idof) {
            rows[idof] = side_elem_gids[side_eq_offsets[idof]];
          }

          if (globalAllowColumnCoupling) {
            // Assume the worst, and couple with all eqns over the whole column
            const int numLayers = cell_layers_data_lid->numLayers;
            const LO basal_elem_LID = cell_layers_data_lid->getColumnId(elem_LID);
            for (int eq=0; eq<neq; ++eq) {
              const auto& eq_offsets = sol_dof_mgr->getGIDFieldOffsets(eq);
              const int num_col_gids = eq_offsets.size();
              cols.resize(num_col_gids);
              for (int il=0; il<numLayers; ++il) {
                const LO layer_elem_lid = cell_layers_data_lid->getId(basal_elem_LID,il);
                const auto& elem_gids = sol_dof_mgr->getElementGIDs(layer_elem_lid);

                for (int jdof=0; jdof<num_col_gids; ++jdof) {
                  cols[jdof] = elem_gids[eq_offsets[jdof]];
                }
                m_jac_factory->insertGlobalIndices(rows(),cols(),true);
              }
            }
          } else {

            // Add local coupling (on this side) with all eqns
            // NOTE: we could be fancier, and couple only with volume eqn or side eqn that are defined
            //       on this side set. However, if a sideset is a subset of another, we might miss the
            //       coupling since the side sets have different names. We'd have to inspect if a ss is
            //       contained in the other, but that starts to get too involved. Given that it's not
            //       a common scenario (need 2+ ss eqn defined on 2 different sidesets), and that we
            //       might have to redo this when we assemble by blocks, we just don't bother.
            for (int col_eq=0; col_eq<neq; ++col_eq) {
              const auto& col_eq_offsets = sol_dof_mgr->getGIDFieldOffsetsSide(col_eq,side_pos);
              const int num_col_gids = col_eq_offsets.size();
              cols.resize(num_col_gids);
              for (int jdof=0; jdof<num_col_gids; ++jdof) {
                cols[jdof] = side_elem_gids[col_eq_offsets[jdof]];
              }

              m_jac_factory->insertGlobalIndices(rows(),cols(),true);
            }
          }
        }
      }
    }
  }

  m_jac_factory->fillComplete();
}