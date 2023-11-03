#include <iostream>

class parent
{
  public:
    parent();
    virtual void printthis();
  protected:
    void secret_print();
};

class child : public parent
{
  public:
    child();
    void printthis() override;
};

parent::parent()
{
    printf("this is parent constructor\n");
}

void
parent::printthis()
{
    printf("parent printing this\n");
}

void
parent::secret_print()
{
    printf("parent's secret\n");
}

child::child()
{
    printf("this is child constructor\n");
}

void
child::printthis()
{
    printf("child printing this\n");
    secret_print();
}

int main()
{
    child test;
    test.printthis();
    return 0;
};

