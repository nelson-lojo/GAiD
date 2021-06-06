import sys
import os
try:
    assert len(sys.argv) > 2
except:
    print("USAGE: runBot <filename> <token>")
    exit()
script = sys.argv[1]
token = sys.argv[2]

# Mostaza's Prophet:
#   NDc5MTU3NDQwNDg3NzUxNjgw.Dl0qVQ.XWF6Nf4kT7J-fsCQ_JccFYIURRw
# GAiD:
#   ODQ3Njk1MDg2ODQ1ODIxMDE5.YLBzkg.b4HhpG-r7NXJ3RmOVYuK7TChzgs

os.system(f"python3 {script} {token}")
