var a int = 3;
var b float = 5.3;
const c = 3.0;
func suma(x float, y float)  float{
	//return x+y;
	print ":D";
	return 3.0;
}
const f = suma(2.0,3.0);
var v float = suma(2.0,suma(3.0,3.3));
func funcion(x float, y float) int {
	print (x+y);
	print b+x;
	x = 7.0;
	if x > b {
		print x;
		print "x es mayor";
		x = b+2.0;

		while x >= b {
			print x;
			x = x-1.0;
			print a;
		}
	}
	else{
		print x;
		print "x es menor";
	}
	//return funcion(funcion(2.0,funcion(1.2,2.3)),funcion(3.3,23.23));
	while x >= b {
		print x;
		x = x-1.0;
		print a;
	}
	//return (3.2+ suma(3.0,32.3));
	a = funcion(3.2,3.0);
	print funcion(2.3,(23.0*3.0));
	print (suma(3.0,suma(3.3,4.0)))+3.0;
	return 0;
}
