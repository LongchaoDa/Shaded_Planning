function getEnvironmentVariable(variableName) {
    if (process.env[variableName]) {
      return process.env[variableName];
    } else {
      throw new Error(`Environment variable ${variableName} is not defined.`);
    }
  }
  
  module.exports = { getEnvironmentVariable };
  