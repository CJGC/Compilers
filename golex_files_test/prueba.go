package func main() {
	
import "fmt"

type persona struct{
	nombre string
	edad int
}

func main(){
	fmt.Println(persona{"crist",40})
	fmt.Println(persona{"sti",10})

	s := persona{nombre:"sean",edad:25}
	fmt.Println(s.nombre)

	sp := &s
	fmt.Println(sp.edad)

	sp.edad = 51
	fmt.Println(sp.age)
}