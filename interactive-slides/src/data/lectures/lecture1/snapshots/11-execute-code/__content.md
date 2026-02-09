## Step 2: Execute Code

Now we execute the generated code using Python's subprocess module to get a reliable computational result.

**Create an execution function:**
```python
import subprocess
import sys

def execute_code(code):
    try:
        # Write code to a temporary file
        with open("generated_code.py", "w") as f:
            f.write(code)

        # Execute
        result = subprocess.run(
            [sys.executable, "generated_code.py"],
            capture_output=True,  # Capture stdout and stderr
            text=True,            # Return output as string (not bytes)
            timeout=10
        )

        return result.stdout if result.returncode == 0 else result.stderr

    except Exception as e:
        return f"Error during execution: {str(e)}"
```

**Execute the generated code:**
```python
execution_result = execute_code(generated_code)
print("\nExecution Result:")
print(execution_result)
```

Output:

```
Execution Result:
87.6
```

Now we have a **reliable result computed by Python**, not guessed by the LLM.

**⚠️ Security Warning:** Executing arbitrary LLM-generated code is dangerous in production. Use sandboxed environments (Docker containers, isolated VMs) in real applications.
