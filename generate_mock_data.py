import random
import datetime

industries = ['Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing', 'Energy', 'Transportation', 'Real Estate']
prefixes = ['Global', 'Tech', 'Smart', 'Future', 'Green', 'Blue', 'Red', 'Alpha', 'Omega', 'Prime', 'Next', 'Ultra']
suffixes = ['Corp', 'Inc', 'Ltd', 'Solutions', 'Systems', 'Holdings', 'Group', 'Enterprises', 'Technologies', 'Innovations']
domains = ['com', 'net', 'org', 'io', 'co']

def generate_company_name():
    return f"{random.choice(prefixes)} {random.choice(suffixes)}"

sql_statements = []
sql_statements.append("INSERT INTO mock_companies (name, industry, revenue_millions, employees, founded_year, website) VALUES")

values_list = []
for _ in range(100):
    name = generate_company_name()
    # Ensure unique names roughly by adding a random number if needed, but for simple mock data just raw is fine
    # Let's make it slightly more unique
    if random.random() > 0.8:
        name += f" {random.randint(1, 99)}"
    
    industry = random.choice(industries)
    revenue = round(random.uniform(0.5, 500.0), 2)
    employees = random.randint(10, 5000)
    founded_year = random.randint(1950, 2024)
    website = f"www.{name.lower().replace(' ', '')}.{random.choice(domains)}"
    
    # Escape single quotes for SQL
    name = name.replace("'", "''")
    
    values_list.append(f"('{name}', '{industry}', {revenue}, {employees}, {founded_year}, '{website}')")

sql_statements.append(",\n".join(values_list) + ";")

print("\n".join(sql_statements))