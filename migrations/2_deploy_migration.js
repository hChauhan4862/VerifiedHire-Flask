const EmployeeManagement = artifacts.require("EmployeeManagement");
const RecruiterManagement = artifacts.require("RecruiterManagement");
const EmployeeInfo = artifacts.require("EmployeeInfo");

 
module.exports = function (deployer) {
  deployer.deploy(EmployeeManagement);
  deployer.deploy(RecruiterManagement);
  deployer.deploy(EmployeeInfo);
};