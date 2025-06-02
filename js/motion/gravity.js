/*
 * Calculates gravitational force between two masses.
 * @param {number} m1 - Mass of first object in kilograms.
 * @param {number} m2 - Mass of second object in kilograms.
 * @param {number} r - Distance between object centers in meters.
 * @returns {number} Gravitational force in Newtons.
 */
function gravitationalForce(m1, m2, r) {
    const G = 6.67430e-11; // m^3 kg^-1 s^-2
    return G * (m1 * m2) / (r ** 2);
}

module.exports = { gravitationalForce };