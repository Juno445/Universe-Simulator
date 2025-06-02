const {
  force,
  mass,
  acceleration,
  velocity
} = require('../motion');

// Newton's First Law
function newtonsFirstLaw(forceValue, velocityValue) {
  if (forceValue === 0) {
    return `Net force is zero; object maintains its velocity of ${velocityValue} m/s.`;
  }
  return `Net force is ${forceValue} N; object will accelerate.`;
}

// Newton's Second Law (compute whichever is missing)
function newtonsSecondLaw({ mass: m, acceleration: a, force: f }) {
  if (typeof f === 'undefined' && m !== undefined && a !== undefined) {
    return force(m, a);           // F = m * a
  }
  if (typeof m === 'undefined' && f !== undefined && a !== undefined) {
    return mass(f, a);            // m = F / a
  }
  if (typeof a === 'undefined' && f !== undefined && m !== undefined) {
    return acceleration(f, m);    // a = F / m
  }
  throw new Error('Please provide any two of: mass, acceleration, force.');
}

// Newton's Third Law
function newtonsThirdLaw(forceValue) {
  return {
    action: forceValue,
    reaction: -forceValue
  };
}

module.exports = {
  newtonsFirstLaw,
  newtonsSecondLaw,
  newtonsThirdLaw
};