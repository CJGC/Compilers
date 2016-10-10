while i < n-1 {
	write(v[i]); print " ";
	if v[i] - v[i+1] > 0 {
		print "Quicksort fallo!";
		write(i);
		print "\n";
	}
	i = i + 1;
}
