from apps.users.models import User
from apps.communes.models import Commune

from apps.users.models import User
from apps.communes.models import Commune

def create_demo_users():
    # S'assure qu'une commune existe
    commune = Commune.objects.first()
    if not commune:
        commune = Commune.objects.create(name="Dakar Plateau", region="Dakar")
        print(f"Commune '{commune.name}' créée.")

    users_data = [
        {
            'email': 'amadou@teranga.sn',
            'phone': '+221771112233',
            'first_name': 'Amadou',
            'last_name': 'Diallo',
            'password': 'passer123',
        },
        {
            'email': 'awa@teranga.sn',
            'phone': '+221774445566',
            'first_name': 'Awa',
            'last_name': 'Ndiaye',
            'password': 'passer123',
        },
        {
            'email': 'moussa@teranga.sn',
            'phone': '+221777889900',
            'first_name': 'Moussa',
            'last_name': 'Sow',
            'password': 'passer123',
        }
    ]

    count = 0
    for data in users_data:
        if not User.objects.filter(email=data['email']).exists() and not User.objects.filter(phone=data['phone']).exists():
            User.objects.create_user(
                email=data['email'],
                phone=data['phone'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=data['password'],
                role=User.Role.CITIZEN,
                commune=commune,
                is_verified=True
            )
            print(f"Citoyen cree : {data['first_name']} {data['last_name']} ({data['phone']})")
            count += 1
        else:
            print(f"Le citoyen {data['first_name']} existe deja.")
            
    print(f"\nTermine ! {count} compte(s) ajoute(s).")

if __name__ == '__main__':
    create_demo_users()
