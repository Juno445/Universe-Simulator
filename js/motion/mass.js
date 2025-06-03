// mass = force / acceleration
function mass(force, acceleration) {
  if (acceleration === 0) throw new Error("Acceleration cannot be zero.");
  return force / acceleration;
}
module.exports = mass;