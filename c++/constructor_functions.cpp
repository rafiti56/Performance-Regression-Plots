#include <iostream>

#include <iostream>
using namespace std;

/* a cosntructor is a special function that will get called 
whenever we create an object of a class */

class Book{
    public:
        //specify attributes
        //only declare variables
        string title;
        string author;
        int pages;


        //This is a constructor
        Book(string aTitle, string aAuthor, int aPages){
            title  =  aTitle;
            author =  aAuthor;
            pages = aPages;
        }
        //It is possible to create multiple constructors

        Book(){
            title= "no title";
            author = "no author";
            pages = 0;
        }
        
    //acts as blueprint/template for "book" datatype
};

int main()
{

    //call class on main loop to use the blueprint to construct it 
    //an object is an instance of the class
    //in this case, this will be a book object which is an isntance of the book class


    //use constructors when we create objects.
    /* Book book1("Lena Patona");
    book1.title = "Lena Patitas Adventures";
    book1.author = "Lena M. Bennet";
    book1.pages = 20;

    cout << book1.title; */

    Book book2("lenosa", "patas", 200);
    cout << book2.author << endl;
    cout <<book2.pages << endl;
    

    Book book3;
    cout << book3.title;
    return 0;
}