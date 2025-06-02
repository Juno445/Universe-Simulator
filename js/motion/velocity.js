function velocity(displacement, time) {
  if (time === 0) throw new Error("Time cannot be zero.");
  return displacement / time;
}
module.exports = velocity;