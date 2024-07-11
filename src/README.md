# ResumeCentralPro (proiect)

- api (aplicatie) - pentru api ul central 
- config (configuratia intiala a proiectului) - filele initiale ale proiectului, face legatura cu posibilele aplicatii

## api: 
- views: folder de API-uri; aici sunt implementate GET, POST, DELETE pentru fiecare instanta
- models: fisier pentru database; sunt definite aici modelele principale pentru a putea fi stocate dupa un template in database
- serializers: transforma schemele din database in obiecte de py
- urls: indica URL-urile aplicatiei (se extind pe cele ale proiectului)  

## config:
- urls: indica URL-urile proiectului
