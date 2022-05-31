import uuid

# Generate a random UUID for our key
private_key = uuid.uuid1()
private_key = "".join(str(private_key).split("-"))

public_key = uuid.uuid4()
public_key = "".join(str(public_key).split("-"))

with open(".key_pair.txt", "w") as f:
    f.write(private_key)
    f.write("\n")
    f.write(public_key)
