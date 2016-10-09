/*In this module we will work with arithmetic :D */

integer_number1 int;
integer_number2 int;

integer_number1 := 50;
integer_number2 := 100;
for integer_number1<integer_number2{
  print("integer_number2 - integer_number1 =",integer_number2-integer_number1);
  integer_number2 := integer_number2-1;
}

floating_number float;
floating_number2 float;

floating_number := 2E+3;
floating_number2 := 1.32E-9;
print("adding two floating numbers: ", floating_number+floating_number2);

Octal_number = 0231; // It is not the correct way to assign a value
hexa_number := 0x01fA23;
decimal_number := 777;

print("I Am not sure if that is correct! ", Octal_number+hexa_number+decimal_number);

const_value const;
const_value := 7;
