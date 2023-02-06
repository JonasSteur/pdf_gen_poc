#!/usr/bin/env groovy

// Shared Jenkins library can be found at https://github.com/vikingco/shared-jenkins-logic
@Library("shared-jenkins-logic@master")

/*******************************/
/*  Project specific settings  */
/*******************************/

PROJECT_NAME = "pdf_gen_poc";
DOCKER_CONTAINER_NAME = PROJECT_NAME;
AWS_REPOSITORY_NAME = PROJECT_NAME;
HELM_CHART_NAME = PROJECT_NAME;

TEST_MAKE_COMMANDS = [
    flake8: "test_flake8",
    black: "test_black",
    isort: "test_isort",
    mypy: "test_mypy",
    python: "test_python",
    migrations: "test_makemigrations"
];

/*******************************/
/*          Constants          */
/*******************************/

SSH_CREDENTIALS_KEY = "jenkins2"; // Key in the Jenkins credentials store that points to the ssh file

ENVIRONMENTS = sharedEnvironments.getEnvironments();

// ENVIRONMENTS[0].deployOnlyFromMaster = false;

properties([
    buildDiscarder(logRotator(daysToKeepStr: "5", numToKeepStr: "10", artifactNumToKeepStr: "1")),
]);

/*******************************/
/*          Pipeline           */
/*******************************/

node {
    timestamps {
        try {
            gitCommit = sharedJenkinsLogic.clone();

            testImage = sharedDockerImages.getDefaultTestImage(DOCKER_CONTAINER_NAME, gitCommit);
            testImage.prebuildTargets = ["requirements_builder"];
            deployImage = sharedDockerImages.getDefaultDeployImage(DOCKER_CONTAINER_NAME, gitCommit);
            deployImage.prebuildTargets = ["requirements_builder"];

            sharedJenkinsLogic.build(SSH_CREDENTIALS_KEY, [testImage, deployImage], false, AWS_REPOSITORY_NAME);
            sharedJenkinsLogic.lint(ENVIRONMENTS, gitCommit, HELM_CHART_NAME, [deployImage]);
            sharedJenkinsLogic.test(TEST_MAKE_COMMANDS, testImage);

            def awsEnvironments = sharedJenkinsLogic.selectDeployEnvironments(ENVIRONMENTS);

            sharedJenkinsLogic.publish(awsEnvironments, [deployImage], AWS_REPOSITORY_NAME, HELM_CHART_NAME, gitCommit);
            sharedJenkinsLogic.generateDeployButtons(awsEnvironments, HELM_CHART_NAME, gitCommit, AWS_REPOSITORY_NAME, [deployImage]);
        } finally {
            sharedJenkinsLogic.cleanup([testImage, deployImage]);
        }
    }
}
