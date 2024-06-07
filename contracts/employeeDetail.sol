// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract EmployeeInfo {
    struct EmployeeBasicInfo {
        string firstName;
        string lastName;
        string email;
        string phone;
        string employeeAddress;
        string filename;
    }

    struct EmployeeWorkingInfo {
        string email;
        string organizationName;
        string designation;
        string responsibility;
        uint256 salary;
        string officeCity;
        uint256 totalExperience;
        string skill;
    }

    struct EmployeeAcademicInfo {
        string email;
        string collegeName;
        string course;
        uint256 score;
        string university;
        string collegeCity;
        uint256 year;
    }

    enum DocumentTypes {
        Education,
        GovtID,
        Files
    }

    struct EmployeeDocument {
        // DocumentTypes documentType;
        string title;
        string document_id;
        string file_name;
        string file_url;
        string json_data;
        string verified_by;
        bool isVerified;
        // uint256 date;
    }

    struct EmployeeEndorestInfo {
        string endoresid;
        string email;
        string endorest;
        string desc;
        string score;
        string status;
        string hasupdated;
        string requestdate;
    }

    struct Employee {
        EmployeeBasicInfo basicInfo;
        EmployeeWorkingInfo workingInfo;
        EmployeeAcademicInfo academicInfo;
        EmployeeDocument[] documentInfo;
        EmployeeEndorestInfo endorestInfo;
    }

    mapping(string => Employee) public employees; // Map email to Employee

    function setBasicInfo(
        string memory _firstName,
        string memory _lastName,
        string memory _email,
        string memory _phone,
        string memory _employeeAddress,
        string memory _filename
    ) public {
        employees[_email].basicInfo = EmployeeBasicInfo(
            _firstName,
            _lastName,
            _email,
            _phone,
            _employeeAddress,
            _filename
        );
    }

    function setWorkingInfo(
        string memory _email,
        string memory _organizationName,
        string memory _designation,
        string memory _responsibility,
        uint256 _salary,
        string memory _officeCity,
        uint256 _totalExperience,
        string memory _skill
    ) public {
        employees[_email].workingInfo = EmployeeWorkingInfo(
            _email,
            _organizationName,
            _designation,
            _responsibility,
            _salary,
            _officeCity,
            _totalExperience,
            _skill
        );
    }

    function setAcademicInfo(
        string memory _email,
        string memory _collegeName,
        string memory _course,
        uint256 _score,
        string memory _university,
        string memory _collegeCity,
        uint256 _year
    ) public {
        employees[_email].academicInfo = EmployeeAcademicInfo(
            _email,
            _collegeName,
            _course,
            _score,
            _university,
            _collegeCity,
            _year
        );
    }

    function addDocument(
        string memory email,
        string memory title,
        string memory document_id,
        string memory file_name,
        string memory file_url,
        string memory json_data,
        string memory verified_by
    ) public {
        employees[email].documentInfo.push(
            EmployeeDocument(
                title,
                document_id,
                file_name,
                file_url,
                json_data,
                verified_by,
                true
            )
        );
    }

    function getProofInfoByEmail(
        string memory _email
    ) public view returns (EmployeeDocument[] memory) {
        return employees[_email].documentInfo;
    }

    function getBasicInfoByEmail(
        string memory _email
    ) public view returns (EmployeeBasicInfo memory) {
        return employees[_email].basicInfo;
    }

    function getWorkingInfoByEmail(
        string memory _email
    ) public view returns (EmployeeWorkingInfo memory) {
        return employees[_email].workingInfo;
    }

    function getAcademicInfoByEmail(
        string memory _email
    ) public view returns (EmployeeAcademicInfo memory) {
        return employees[_email].academicInfo;
    }

    function updateSkillByEmail(
        string memory _email,
        string memory _newSkill
    ) public {
        employees[_email].workingInfo.skill = _newSkill;
    }

    EmployeeEndorestInfo[] public allEndorestments; // Track all endorestments

    // Function to set endorestment info
    function setEndorestInfo(
        string memory _endoresid,
        string memory _email,
        string memory _endorest,
        string memory _desc,
        string memory _score,
        string memory _status,
        string memory _hasupdated,
        string memory _requestdate
    ) public {
        employees[_email].endorestInfo = EmployeeEndorestInfo(
            _endoresid,
            _email,
            _endorest,
            _desc,
            _score,
            _status,
            _hasupdated,
            _requestdate
        );

        // Add endorestment to allEndorestments array
        allEndorestments.push(
            EmployeeEndorestInfo(
                _endoresid,
                _email,
                _endorest,
                _desc,
                _score,
                _status,
                _hasupdated,
                _requestdate
            )
        );
    }

    // Function to get endorestment info by email
    function getEndorestInfoByEmail(
        string memory _email
    ) public view returns (EmployeeEndorestInfo memory) {
        return employees[_email].endorestInfo;
    }

    // Function to get all endorestments
    function getAllEndorestInfo()
        public
        view
        returns (EmployeeEndorestInfo[] memory)
    {
        return allEndorestments;
    }

    function getEndorestInfoByEndorestId(
        string memory _endorestid
    ) public view returns (EmployeeEndorestInfo memory) {
        for (uint i = 0; i < allEndorestments.length; i++) {
            if (
                keccak256(abi.encodePacked(allEndorestments[i].endoresid)) ==
                keccak256(abi.encodePacked(_endorestid))
            ) {
                return allEndorestments[i];
            }
        }

        revert("Endorestment not found");
    }

}
