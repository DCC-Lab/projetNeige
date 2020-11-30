from .DatabaseConfigModel import DatabaseConfigModel

localhost_database_config = DatabaseConfigModel("localhost", 32000, "projetneigedb", "projetNeige", "pn2020")
internal_databse_config = DatabaseConfigModel("192.168.2.28", 1433, "projetneigedb", "projetNeige", "pn2020")
remote_database_config = DatabaseConfigModel("70.55.117.196", 1433, "projetneigedb", "projetNeige", "pn2020")


