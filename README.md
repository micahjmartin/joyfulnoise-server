# JOYFULNOISE Server
Joynoise is created to return commands to calling back C2's. This server
can integrate into [Arsenal](https://github.com/kcarretto/Arsenal)
for primitave C2 from the program


### Deployment
```
git clone https://github.com/micahjmartin/joyfulnoise-server
cd joyfulnoise-server
docker build -t jf-c2 .
docker run -d -p 80:80 --name ArsenalC2 jf-c2
```
