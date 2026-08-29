# Public Datasets

## CICIDS2017
The CICIDS2017 dataset contains benign and the most up-to-date common attacks.
**Obtaining:** Download from the Canadian Institute for Cybersecurity (CIC) at UNB.
**Limitations:** Features need to be normalized to our `NetworkEvent` schema. Simulated attacks might not reflect all nuances of a living enterprise network graph over long periods.

## UNSW-NB15
Network intrusion dataset.
**Obtaining:** Download from UNSW Canberra Cyber.
**Limitations:** Different feature set from CICIDS2017, must map common protocol/bytes/duration fields to our schema.
