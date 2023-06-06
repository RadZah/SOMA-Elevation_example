from soma import *

soma = Soma(population_size=15)

coordinates = {
    "latt_min": 49.372811084755405,
    "latt_max": 49.67105062948057,
    "long_min": 17.94719292783253,
    "long_max": 18.541577721121097
}
soma.set_area(coordinates)
# soma.DEBUG_MODE = True

print("\nSOMA algorithm started... wait for it...")
result = soma.run()

print("\nFinished SOMA algorithm")

print("\nResult:")
print(result)

print("Finished")