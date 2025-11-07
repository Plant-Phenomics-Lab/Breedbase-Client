from client import BrAPIClient
client = BrAPIClient()

client.show_all_services_help()
client.general_get(service="attributes")
client.general_get(service="observations",
                   pagesize=10,
                   max_pages=1)