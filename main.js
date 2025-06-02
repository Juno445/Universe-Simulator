// Newtowns Laws
const {
newtonsFirstLaw,
newtonsSecondLaw,
newtonsThirdLaw
} = require('./laws');

// Motion 
const {
acceleration,
force,
mass,
velocity,
displacement,
time 
} = require('./motion');

console.log(acceleration(10, 2));                // 5
console.log(force(2, 5));                        // 10
console.log(mass(10, 2));                        // 5
console.log(velocity(100, 10));                  // 10
console.log(displacement(10, 10));               // 100
console.log(time(100, 20));                      // 5

console.log(newtonsFirstLaw(0, 5));              // Net force is zero; object maintains its velocity of 5 m/s.
console.log(newtonsFirstLaw(10, 5));             // Net force is 10 N; object will accelerate.
console.log(newtonsSecondLaw({ mass: 2, acceleration: 5 }));  // 10 (force)
console.log(newtonsSecondLaw({ force: 10, acceleration: 5 })); // 2 (mass)
console.log(newtonsSecondLaw({ force: 10, mass: 2 }));        // 5 (acceleration)
console.log(newtonsThirdLaw(15));                 // { action: 15, reaction: -15 }