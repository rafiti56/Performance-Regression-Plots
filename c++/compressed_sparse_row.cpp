#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct Sparse_CSR {
    size_t n_rows;
    size_t n_cols;
    size_t n_nz;
    size_t* row_ptrs;
    size_t* col_indices;
    double* values;
} Sparse_CSR;


int create_sparse_csr(
    const double* A,
    size_t n_rows,
    size_t n_cols,
    size_t n_nz,
    Sparse_CSR* A_csr
);

int print_sparse_csr(const Sparse_CSR* A_CSR);

int matrix_vector_sparse_csr(
    const Sparse_CSR* A_coo,
    const double* vec,
    double* res

);

int free_sparse_csr(Sparse_CSR* A_CSR);

int main(int argc, char** __argv){
    size_t n_rows  =5;
    size_t n_cols = 5;
    size_t n_nz = 12;

    double A[] = {
        1,0,0,2,0,
        3,4,2,5,0,
        5,0,0,8,17,
        0,0,10,16,0,
        0,0,0,0,14
    };
    double x[] ={
        1,
        2,
        3,
        4,
        5
    };

    double Ax[5];

    Sparse_CSR A_csr;

    create_sparse_csr(A, n_rows, n_cols, n_nz, &A_csr);

    return EXIT_SUCCESS;
}

int create_sparse_csr(
    const double* A,
    size_t n_rows,
    size_t n_cols,
    size_t n_nz,
    Sparse_CSR* A_csr
) {
    A_csr->n_rows = n_rows;
    A_csr->n_cols = n_cols;
    A_csr->n_nz = n_nz;
    A_csr->row_ptrs = calloc(n_rows + 1, sizeof(size_t));
    A_csr->col_indices = calloc(n_nz, sizeof(size_t));
    A_csr->values = calloc(n_nz, sizeof(double));

    size_t nz_id = 0;

    

    for (size_t i=0; i<n_rows; ++i){
        A_csr->row_ptrs[i] = nz_id;
        for (size_t j=0; j<n_cols; ++j){
            if (A[i*n_cols +j] !=0){
            A_csr->col_indices[nz_id] =j;
            A_csr->values[nz_id] = A[i*n_cols + j];
            ++nz_id;
            }

        }
    }
    
    A_csr->row_ptrs[n_rows] = nz_id;


    return EXIT_SUCCESS;
}