// Force * Mass

function acceleration(force, mass) {
  if (mass === 0) throw new Error("Mass cannot be zero.");
  return force / mass;
}
module.exports = acceleration;