import org.junit.Test
import org.junit.Assert.*

class CalculatorTest {
    
    @Test
    fun testAddTwoNumbers() {
        val calculator = Calculator()
        val result = calculator.add(5, 3)
        assertEquals(8, result)
    }
    
    @Test
    fun testAddNegativeNumbers() {
        val calculator = Calculator()
        val result = calculator.add(-5, -3)
        assertEquals(-8, result)
    }
    
    @Test
    fun testAddZero() {
        val calculator = Calculator()
        val result = calculator.add(5, 0)
        assertEquals(5, result)
    }
}

class Calculator {
    fun add(a: Int, b: Int): Int {
        return a + b
    }
} 