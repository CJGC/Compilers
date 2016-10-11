func quicksort(l int, r int, a int[8192]) {
	
	var i int = l;
	var j int = r;
	var x int = a[(l+r)/2];
	var done int = 0;

	while done == 0 {
		while a[i] < x {
			i = i + 1;
		}
		while x < a[j] {
			j = j - 1;
		}
		if i <= j {
			var vmp int = a[i];
			a[i] = a[j];
			a[j] = tmp;
			i = i + 1;
			j = j - 1;
		}
		if i < j {
			done = 1;
		}
	}

	if l < j {
		quicksort(l,j,a);
	}
	if i < r {
		quicksort(i,r,a);
	}
}

var v int[8192];
var i int = 0;
var j int;

print "Entre n:";
read(n);

while i < n{
	read(v[i]);
	i = i + 1;
}
quicksort(0,n-1,v);

i = 0;
while i < n-1 {
	write(v[i]); print " ";
	if v[i] - v[i+1] > 0 {
		print "Quicksort fallo";
		write(i);
		print "\n";
	}
	i = i + 1;
}
write(v[i]);
print "Finalizo con exito!\n";
