# ResumeCentralPro (proiect)

- resumeApi (aplicatie) - pentru api ul central 
- resumeCentralPro (configuratia intiala a proiectului) - filele initiale ale proiectului, face legatura cu posibilele aplicatii

## resumeApi: 
- views: folder de api uri, aici sunt implementate GET,POST,DELETE pentru fiecare instanta
- models: fisier pentru database, sunt definite aici modelele principale pentru a putea fi stocate dupa un template in db 
- serializers: transforma schemele din db in obiecte de py  
- urls: indica url urile aplicatiei (se extind pe cele ale proiectului)  

## resumeCentralPro:
- urls: indica url urile proiectului
