Deloitte Challenge

EQUIP --> DEBUGGING DIVAS --> Ivan Ramírez, Daniel Aagaard, Bruna Colomer i Daniel Fernández

https://github.com/brunacolomer/deloitte-datasets

Aquesta es la nostra proposta per al challenge de Deloitte a la UABHack

1. Tractament de les dades

Els document que hem tingut en compte han sigut els següents:
Transport Públic Barcelona.xlsx
Densitat Població Barcelona 2021.xlsx
Resum dades mensuals i diàries de viatgers FMB 2025_1er Semestre.xlsx
Municipis de les comarques.xlsx
Parades Bus Barcelona.xlsx
Parades Taxi Barcelona.xlsx

D’aquestes dades hem pogut extreure les zones amb més densitat de població, així com les línies amb més concurrència, essent aquestes últimes la L1, L3 i L5.

Amb aquestes dades hem pogut generar el mapa amb el sistema de metro, així com un mapa que marca els punts centrals de cada regió per facilitar el càlcul de les zones amb més densitat de cara a afegir noves estacions.


2. Metodologia de treball

El primer que hem fet ha sigut analitzar el problema entre tots els membres de l’equip per trobar una solució óptima.

Una vegada vam tenir la idea principal, ens vam posar a investigar les diferents tecnologies que emprariem per a poder realitzar la criba de dades així com la pròpia aplicació, entre les quals vam escollir google collab per a fer les primeres probes, python, react i fastapi.

Una vegada teniem les tecnologies, dos membres han començat a netejar les dades disponibles i a buscar noves dades mentre els altres dos han començat a desenvolupar el mapa que ens permet visualitzar les línies de metro.

Després la metodologia ha consistit en generar tasques i anar resolent-les entre els membres de l'equip rotant entre les diferents necessitats del projecte.


3. Proposta plantejada

La nostra proposta consisteix en el desenvolupament d’un sistema intel·ligent capaç d’analitzar i suggerir possibles ampliacions de la xarxa de metro de Barcelona. El sistema rep com a entrada un conjunt de dades en format CSV que conté informació rellevant sobre la densitat de població i la dificultat de construcció de cada zona del territori. A més, tenim un altre fitxer amb la ubicació i característiques de les estacions ja existents.

A partir d’aquestes dades, l’algoritme és capaç d’identificar quines àrees presenten una major necessitat de cobertura i quines ofereixen condicions més favorables per a l’expansió de la línia. D’aquesta manera, el sistema proposa quina seria la direcció o el traçat més adequat per estendre la xarxa actual, equilibrant factors com la demanda del servei, el cost i viabilitat de construcció i la connectivitat amb altres regions amb una gran densitat de població.

La idea també és que l’estació es col·loqui en un lloc en el que no hi hagin altres mètodes de transport públics (taxi o bus) a prop del nou punt.

A més, el sistema incorpora un visualitzador de mapa interactiu que permet a l’usuari ajustar els paràmetres de prioritat segons els seus objectius. Per exemple, es pot donar més pes a la densitat de població, o prioritzar la facilitat constructiva si es busca reduir costos. 

Les llibreries que hem emprat per a la neteja i extracció de dades i per la representació del mapa han estat pandas i plotly respectivament.

Finalment, el projecte pretén oferir una eina útil per ajudar a prendre decisions més informades i basades en dades reals. En el futur, el sistema podria integrar altres fonts d’informació per aconseguir resultats encara més precisos i realistes.


