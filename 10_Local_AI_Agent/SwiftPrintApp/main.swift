// ================================
//  Simple Swift Print Program
// ================================

// --- 1. Print a simple string ---
print("Hello, World!")

// --- 2. Print multiple values ---
print("Name:", "John", "Age:", 30)

// --- 3. Print with string interpolation ---
let name = "Swift"
let version = 5.9
print("Welcome to \(name) version \(version)!")

// --- 4. Print with custom separator and terminator ---
print("Apple", "Banana", "Cherry", separator: " | ", terminator: "\n")

// --- 5. Print without newline at the end ---
print("Loading", terminator: "")
print("... Done!")

// --- 6. Print multiple lines using a multiline string ---
let multiline = """
    This is line 1
    This is line 2
    This is line 3
    """
print(multiline)

// --- 7. Print from a function ---
func printMessage(_ message: String) {
    print("[INFO]: \(message)")
}

printMessage("Program finished successfully!")
