from app import app, seed
if __name__ == '__main__':
    with app.app_context():
        seed()
        print('Seed complete. Admin: admin/admin | Teachers: turing,hoppper (teacher) | Students: alice,bob,charlie (student)')
