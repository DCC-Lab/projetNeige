## Data Guidelines

Each measure (on 15sec timestamps) made of a burst of 1000 acquisitions of some milliseconds. This allowed us to keep the detector close to saturation, but still acquire enough data to make statistics (mean and standard deviation). Thus, a measure comes with a mean and a standard deviation, because it represents a distribution of measures.

Each detector communicated to a central server on the field. This server sent the data via 2G to a custom 2G server here in Quebec (RaspeberryPy with a 2G Shield). This server was connected to the internet, which sent the data to the database server, where the data was being stored. For Ease-Of-Use only, and because the different engineers built the systems at different time, the format of the data was the one you see in the table &quot;DetectorUnitData&quot;.

Afterwards, the database server saved this data, but converted it to a more humanreadable table + calculated the irradiance and included it in another table &quot;PhotodiodeData&quot;
|indicator|description|
|-|-|
| id | UUID given to each row. It is used as a PRIMARY KEY |
| unit\_id | unit identification number [1, 8] |
| pd\_id | photodiode identification number inside an unit [1, 4] |
| timestamp | time UTC Montreal/Toronto |
| location | S = Shrubs(dans les buissons), F = Field (dans la plaine) |
| height | height in (mm) |
| wavelength | spectral region of transmittance of the filters on the photodiode |
| powerMean | Typo, irradiance in (W/m^2) |
| powerStd | standard deviation of irradiance (W/m^2) |
| DigitalNumber(DN) Mean | RAWDATA: Digital Value Mean of the ADC (AnalaogToDigitalConverter) before conversion in irradiance. |
| DigitalNumber(DN) SD | RAWDATA: Standard deviation for the DN Mean |

- Unit == Circuit with 4 photodiodes
- RelatedClusterName == location
- pd1 == photodiode= with id 1
