function time(displacement, velocity) {
  if (velocity === 0) throw new Error("Velocity cannot be zero.");
  return displacement / velocity;
}
module.exports = time;