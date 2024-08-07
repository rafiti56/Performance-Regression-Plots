/*
.BCRS Sparse Matrix Chatgpt Example
*/

#include <iostream>
#include <vector>
#include <cmath>

using namespace std;

// BlockCRS Matrix Class
class BlockCRSMatrix {
public:
    // Constructor
    BlockCRSMatrix(int numRows, int numCols, int blockSize)
        : numRows(numRows), numCols(numCols), blockSize(blockSize) {
        int numBlocksRow = (numRows + blockSize - 1) / blockSize;
        int numBlocksCol = (numCols + blockSize - 1) / blockSize;
        values.resize(numBlocksRow);
        colIndices.resize(numBlocksRow);
        rowPtr.resize(numBlocksRow + 1, 0);
    }

    void addBlock(int rowStart, int colStart, const vector<vector<double>>& block) {
        int rowIndex = rowStart / blockSize;
        int colIndex = colStart / blockSize;

        values[rowIndex].push_back(block);
        colIndices[rowIndex].push_back(colIndex);

        rowPtr[rowIndex + 1] += 1;
    }

    void adjustRowPtr() {
        for (size_t i = 1; i < rowPtr.size(); ++i) {
            rowPtr[i] += rowPtr[i - 1];
        }
    }

    void print() const {
        for (int i = 0; i < rowPtr.size() - 1; ++i) {
            cout << "Row " << i << ": ";
            for (int j = 0; j < values[i].size(); ++j) {
                cout << "[Block at column " << colIndices[i][j] << "] ";
                for (const auto& row : values[i][j]) {
                    for (double val : row) {
                        cout << val << " ";
                    }
                    cout << "| ";
                }
                cout << " ";
            }
            cout << endl;
        }
    }

private:
    int numRows; // Number of rows in the matrix
    int numCols; // Number of columns in the matrix
    int blockSize; // Size of each block (blockSize x blockSize)
    vector<vector<vector<vector<double>>>> values; // Values of the blocks
    vector<vector<int>> colIndices; // Column indices of the blocks
    vector<int> rowPtr; // Row pointers for CRS format
};

// Function to check if a block is empty
bool isBlockEmpty(const vector<vector<double>>& block) {
    for (const auto& row : block) {
        for (double val : row) {
            if (val != 0.0) {
                return false;
            }
        }
    }
    return true;
}

// Function to divide a large matrix into blocks and store in BlockCRSMatrix
void divideAndStoreBlocks(const vector<vector<double>>& largeMatrix, int blockSize, BlockCRSMatrix& blockMatrix) {
    int numRows = largeMatrix.size();
    int numCols = largeMatrix[0].size();

    for (int i = 0; i < numRows; i += blockSize) {
        for (int j = 0; j < numCols; j += blockSize) {
            vector<vector<double>> block(blockSize, vector<double>(blockSize, 0));
            for (int bi = 0; bi < blockSize; ++bi) {
                for (int bj = 0; bj < blockSize; ++bj) {
                    if (i + bi < numRows && j + bj < numCols) {
                        block[bi][bj] = largeMatrix[i + bi][j + bj];
                    }
                }
            }
            if (!isBlockEmpty(block)) {
                blockMatrix.addBlock(i, j, block);
            }
        }
    }

    // Adjust rowPtr to be cumulative
    blockMatrix.adjustRowPtr();
}

int main() {
    // Define a sparse large matrix (example 6x6 matrix)
    vector<vector<double>> largeMatrix = {
        {1, 0, 3, 0, 0, 6},
        {0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0},
        {0, 0, 21, 22, 0, 0},
        {31, 32, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0}
    };

    int blockSize = 2;

    // Create a Block CRS Matrix
    BlockCRSMatrix blockMatrix(largeMatrix.size(), largeMatrix[0].size(), blockSize);

    // Divide the large matrix into blocks and store in BlockCRSMatrix
    divideAndStoreBlocks(largeMatrix, blockSize, blockMatrix);

    // Print the matrix
    blockMatrix.print();

    return 0;
}
