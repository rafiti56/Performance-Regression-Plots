#include <iostream>
#include <string>
using namespace std;

int main()
{
    int age = 19; //stored inside containers in memory
    double gpa = 2.7; //each container has a specific memory address
    string name = "Mike";

    //can create a variable that stores the pointer "pointer variable"
    int *pAge = &age;
    // * is used to create variables "container" that store pointers
    //container uses datatype of the variable that it is pointing to
    double *pGpa = &gpa;

    string *pname = &name;

    cout << age << endl;
    //print memory address (hexadecimal number)
    cout << pAge << endl;



    //dereferencing a pointer: grab the value inside the memory address
    cout<< *pAge;


    // & is a pointer to the address in which the specified variable is stored
    return 0;

   


}

/* Random Access Memory (RAM) stores the variables in the RAM to store and keep 
track of information
when you create a varibale and give it a value, the program takes the values and
stores it inside of the memory inside the computer */

//computer accesses the variable through the physical memory address