#include <iostream>
using namespace std;


class Book{
    public:
        //specify attributes
        //only declare variables
        string title;
        string author;
        int pages;
        
    //acts as blueprint/template for "book" datatype
};

int main()
{

    //call class on main loop to use the blueprint to construct it 
    //an object is an instance of the class
    //in this case, this will be a book object which is an isntance of the book class

    Book book1;
    book1.title = "Lena Patitas Adventures";
    book1.author = "Lena M. Bennet";
    book1.pages = 20;

    cout << book1.title;
    
    return 0;
}