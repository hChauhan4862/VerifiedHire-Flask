// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract RecruiterManagement {
    struct Recruiter {
        string name;
        string email;
        string password;
        string phone;
        string company;
        string admin;
    }

    mapping(string => Recruiter) public recruiters;
    mapping(string => bool) public emailExists;

    event RecruiterRegistered(string email);
    event RecruiterLoggedIn(string email);

    string[] public recruiterKeys;

    function registerRecruiter(
        string memory _name,
        string memory _email,
        string memory _password,
        string memory _phone,
        string memory _company,
        string memory _admin
    ) external {
        require(
            bytes(recruiters[_email].email).length == 0,
            "Email already registered"
        );

        Recruiter memory newRecruiter = Recruiter(
            _name,
            _email,
            _password,
            _phone,
            _company,
            _admin
        );
        recruiters[_email] = newRecruiter;
        recruiterKeys.push(_email);
    }

    function getAllRecruiters() public view returns (Recruiter[] memory) {
        uint256 count = recruiterKeys.length;
        Recruiter[] memory allRecruiters = new Recruiter[](count);
        for (uint256 i = 0; i < count; i++) {
            allRecruiters[i] = recruiters[recruiterKeys[i]];
        }
        return allRecruiters;
    }

    function recruiterLogin(
        string memory _email,
        string memory _password
    ) external returns (bool) {
        require(
            keccak256(bytes(recruiters[_email].password)) ==
                keccak256(bytes(_password)),
            "Incorrect password"
        );
        emit RecruiterLoggedIn(_email);
        return true;
    }

    function getRecruiterByEmail(
        string memory _email
    )
        external
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        Recruiter memory recruiter = recruiters[_email];
        return (
            recruiter.name,
            recruiter.email,
            recruiter.password,
            recruiter.phone,
            recruiter.company,
            recruiter.admin
        );
    }

    function updateAdmin(
        string memory _email,
        string memory _newAdmin
    ) external {
        require(
            bytes(recruiters[_email].email).length != 0,
            "Recruiter not found"
        );
        recruiters[_email].admin = _newAdmin;
    }

    struct VerificationRecord {
        string recname;
        string company;
        string recemail;
        string uid;
        string vftime;
    }

    VerificationRecord[] public verificationRecords;

    function addVerificationRecord(
        string memory _recname,
        string memory _company,
        string memory _recemail,
        string memory _uid,
        string memory _vftime
    ) external {
        VerificationRecord memory newRecord = VerificationRecord(
            _recname,
            _company,
            _recemail,
            _uid,
            _vftime
        );
        verificationRecords.push(newRecord);
    }

    function getAllVerificationRecords()
        public
        view
        returns (VerificationRecord[] memory)
    {
        return verificationRecords;
    }
}

contract EmployeeManagement {
    struct Employee {
        string name;
        string email;
        string password;
        string phone;
        string uid;
    }

    mapping(string => Employee) public employees;
    mapping(string => bool) public emailExists;
    mapping(string => bool) public loggedIn;
    mapping(string => uint256) public loginTime;
    mapping(string => string) public uidToEmail; // Mapping from UID to email
    uint256 public employeeCount;

    event EmployeeRegistered(string email);
    event EmployeeLoggedIn(string email);
    event LoginLogAdded(string email, uint256 loginTime);

    string[] public employeeKeys;

    function registerEmployee(
        string memory _name,
        string memory _email,
        string memory _password,
        string memory _phone,
        string memory _uid
    ) external {
        require(
            bytes(employees[_email].email).length == 0,
            "Email already registered"
        );

        Employee memory newEmployee = Employee(
            _name,
            _email,
            _password,
            _phone,
            _uid
        );
        employees[_email] = newEmployee;
        employeeKeys.push(_email);

        // Update uidToEmail mapping
        uidToEmail[_uid] = _email;

        emit EmployeeRegistered(_email);
    }

    function getAllEmployees() public view returns (Employee[] memory) {
        uint256 count = employeeKeys.length;
        Employee[] memory allEmployees = new Employee[](count);
        for (uint256 i = 0; i < count; i++) {
            allEmployees[i] = employees[employeeKeys[i]];
        }
        return allEmployees;
    }

    function employeeLogin(
        string memory _email,
        string memory _password
    ) external {
        require(
            keccak256(bytes(employees[_email].password)) ==
                keccak256(bytes(_password)),
            "Incorrect password"
        );

        emit EmployeeLoggedIn(_email);
    }

    function addLoginLog(string memory _email, uint256 _loginTime) external {
        loggedIn[_email] = true;
        loginTime[_email] = _loginTime;
        emit LoginLogAdded(_email, _loginTime);
    }

    function getEmployeeByEmail(
        string memory _email
    )
        external
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        Employee memory employee = employees[_email];
        return (
            employee.name,
            employee.email,
            employee.password,
            employee.phone,
            employee.uid
        );
    }

    function getEmployeeByUid(
        string memory _uid
    )
        external
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        string memory email = uidToEmail[_uid];
        Employee memory employee = employees[email];
        return (
            employee.name,
            employee.email,
            employee.password,
            employee.phone,
            employee.uid
        );
    }

    function getEmailByUID(
        string memory _uid
    ) external view returns (string memory) {
        return uidToEmail[_uid];
    }
}
