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
    
    // Missing test documentation
    @Test
    fun testLargeNumbers() {
        val calc = Calculator()  // Short variable name
        val x = 1000000  // Magic number
        val y = 2000000  // Magic number
        val z = calc.add(x, y)
        assertEquals(3000000, z)
    }
}

class Calculator {
    // Missing documentation
    fun add(a: Int, b: Int): Int {
        // Inconsistent indentation
      return a + b  // Wrong indentation
    }
    
    // Unused function
    fun unusedFunction() {
        println("This function is never called")  // Print statement in production code
    }
    
    // Function with too many parameters
    fun complexCalculation(a: Int, b: Int, c: Int, d: Int, e: Int, f: Int, g: Int, h: Int, i: Int, j: Int): Int {
        return a + b + c + d + e + f + g + h + i + j  // Very long line
    }
    
    // Function with potential division by zero
    fun divide(a: Int, b: Int): Int {
        return a / b  // No error handling for division by zero
    }
    
    // Function with hardcoded values
    fun calculateTax(amount: Double): Double {
        return amount * 0.15  // Magic number for tax rate
    }
} 