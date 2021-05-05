echo "Removing old key pairs"
rm key-*-{A,B}

echo "Generating a key pair"
python3 rsa.py gen-key-pair


echo -e "\nEnter a phrase:"
read phrase

echo -e "\n\nEncrypting '$phrase' using both key parts"
encA=$(echo "$phrase" | python3 rsa.py encrypt key-1-A)
encB=$(echo "$phrase" | python3 rsa.py encrypt key-1-B)
echo "$phrase -- encryption by A --> $encA"
echo "$phrase -- encryption by B --> $encB"

echo -e "\n\nDecrypting both key parts"
decA=$(echo "$encA" | python3 rsa.py decrypt key-1-B)
decB=$(echo "$encB" | python3 rsa.py decrypt key-1-A)
echo "$encA -- decrypted by B --> $decA"
echo "$encB -- decrypted by A --> $decB"
