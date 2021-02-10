// Packaging validation for supported GNU/Linux systems.

// Note: To work on this script without having to push a commit each
// time, use the jenkins-cli command (see:
// https://wiki.savoirfairelinux.com/wiki/Jenkins.jami.net#Usage_CLI_de_Jenkins).

pipeline {
    agent {
        label 'guix'
    }

    environment {
        BATCH_MODE = 1                 // do no show progress during downloads
        TARBALLS = '/opt/ring-contrib' // set the cache directory
    }

    stages {
        stage('Fetch submodules') {
            steps {
                sh 'git submodule update --init --recursive daemon lrc client-gnome'
            }
        }

        stage('Generate release tarball') {

            agent {
                dockerfile {
                    filename 'docker/Dockerfile_create_release'
                    args "-e TARBALLS -v $TARBALLS:$TARBALLS"
                }
            }
            steps {
                // The selection of the bundled tarballs included in
                // the release tarball depend on what system libraries
                // are provided by the host.  To ensure a single
                // release tarball can be shared the different
                // GNU/Linux distributions supported, generate it in a
                // minimal environment, so that all potentially
                // required libraries are bundled.
                sh 'make release-tarball'
            }
        }

        stage('Build packages') {
            steps {
                // TODO: Parallelize all targets
                sh "make -f Makefile.packaging package-ubuntu_20.04" \
                +  " DISABLE_CONTRIB_DOWNLOADS=TRUE"
            }
        }
    }
}

// packaging-validation-gnulinux

// stage('Packaging validation') {
//     if (env.PACKAGING_TARGET ==~ /rhel/) {
//         // This password is only required for the RHEL packaging task.
//         withCredentials([string(credentialsId: 'developers-redhat-com', variable: 'PASS')])
//         {
//             stage (env.PACKAGING_TARGET) {
//                 build job: 'packaging-validation-gnulinux-generic',
//                 parameters: [string(name: 'GERRIT_REFSPEC', value: env.GERRIT_REFSPEC),
//                              string(name: 'PACKAGING_TARGET', value: env.PACKAGING_TARGET)]
//             }
//         }
//     } else {
//         stage (env.PACKAGING_TARGET) {
//             build job: 'packaging-validation-gnulinux-generic',
//             parameters: [string(name: 'GERRIT_REFSPEC', value: env.GERRIT_REFSPEC),
//                          string(name: 'PACKAGING_TARGET', value: env.PACKAGING_TARGET)]
//             }
//     }
// }

// -----------------

// packaging-validation-gnulinux-generic

// if [ -z "${PACKAGING_TARGET}" ]; then
// 	echo "Error: mandatory PACKAGING_TARGET environment variable not set"
//     exit 1
// fi

// export BATCH_MODE=1
// export GIT_SSL_NO_VERIFY=true
// export RING_CONTRIB_TARBALLS=/opt/ring-contrib

// ###########################
// ## FETCH PROJECT SOURCES ##
// ###########################

// git clone --depth=1 https://${RING_GERRIT_URL}/ring-project
// cd ring-project

// if [ ! -z "${GERRIT_REFSPEC}" ]; then
//     git fetch origin ${GERRIT_REFSPEC} && git checkout FETCH_HEAD
// else
// 	echo "FAILED: I don't know what to build"
//     exit 1
// fi

// export PROJECT_DIR=$(pwd)
// export DAEMON_DIR=$(pwd)/daemon

// # Checkout all submodules to their latest commit.
// git submodule update --init --recursive daemon lrc client-gnome

// ##################################
// ## Install pre-fetched tarballs ##
// ##################################

// if [ -d "${RING_CONTRIB_TARBALLS}" ]; then
// 	cp ${RING_CONTRIB_TARBALLS}/* ${DAEMON_DIR}/contrib/tarballs/ || echo 'No tarballs cache'
// fi


// ###################
// ## Run packaging ##
// ###################

// cd ${PROJECT_DIR}
// make -f Makefile.packaging ${PACKAGING_TARGET}

// -----------------------------------
// daemon-gnulinux

// node(env.JobNode) {
//     def tarballsDir = '/opt/ring-contrib'
//     def tarballsCacheExist = sh returnStatus: true, script: "test -d '${tarballsDir}'"
//     tarballsCacheExist = tarballsCacheExist == 0

//     // Get number of CPU available for the build
//     def cpuCount = sh returnStdout: true, script: 'nproc || echo -n 4'

//     stage('SCM Checkout') {
//         // Wipe workspace and fetch ring-daemon
//         checkout changelog: true, poll: false,
//             scm: [$class: 'GitSCM',
//                 branches: [[name: 'FETCH_HEAD']],
//                 doGenerateSubmoduleConfigurations: false,
//                 extensions: [
//                     [$class: 'CloneOption', noTags: true, reference: '', shallow: true],
//                     [$class: 'WipeWorkspace']],
//                 submoduleCfg: [],
//                 userRemoteConfigs: [[refspec: '${GERRIT_REFSPEC}', url: 'https://${RING_GERRIT_URL}/ring-daemon']]]
//     }


//     stage('Building Docker Image') {
//         //docker.withRegistry('https://registry.hub.docker.com', 'hub.docker.com') {
//             docker.build('daemon-validation', "-f docker/${Dockerfile} .")
//         //}
//     }

//     def jenkinsUID = sh(returnStdout: true, script: 'id -u jenkins').replaceAll("\n", '').trim()
//     def jenkinsGID = sh(returnStdout: true, script: 'id -g jenkins').replaceAll("\n", '').trim()
//     def jenkinsUser = jenkinsUID+':'+jenkinsGID

//     docker.image('daemon-validation').withRun('--privileged -t -u '+jenkinsUser+' -v '+pwd()+':/foo:rw -v '+tarballsDir+':/foo/contrib/tarballs:rw -w /foo -e BATCH_MODE=1', '/bin/bash') {
//         container -> code:{
//             def base_cmd = 'docker exec '+container.id+" sh -c '"
//             def exec_cmd = { cmd -> sh script:base_cmd+cmd+"'" }

//             stage('Setup Contribs') {
//                 exec_cmd('''
//                     cd contrib
//                     mkdir native
//                     cd native
//                     ../bootstrap
//                     make list
//                     make fetch
//                 ''')
//             }

//             stage('Build Contribs') {
//                 exec_cmd("make -Ccontrib/native -j${cpuCount}")
//             }

//             stage('Setup Daemon') {
//                 exec_cmd("./autogen.sh && ./configure --disable-shared --enable-debug")
//             }

//             stage('Build Daemon') {
//                 exec_cmd("make --stop -j${cpuCount} V=1 && test -f ./bin/dring")
//             }

//             stage('Tests') {
//                 // Do only UnitTests and SIP tests that don't require valid external resources
//                 exec_cmd("""
//                     # ok
//                     (cd test/unitTest/ && make -j ut_fileTransfer && ./ut_fileTransfer)
//                     (cd test/unitTest/ && make -j ut_scheduler && ./ut_scheduler)
//                     (cd test/sip/ && make --no-print-directory VERBOSE=1 check)
//                     # To check
//                     #(cd test/unitTest/ && make -j ut_call && ./ut_call || true)
//                     """)
//             }
//         }
//     }
// }

// -------------------------------

// node('ring-buildmachine-02.mtl.sfl') {
//     currentBuild.displayName += ' - ' + env.DISTRIBUTION
//     environment {
//         PASS = credentials('developers-redhat-com')
//     }

//     // Script configuration
//     def sshPrivateKey = '/var/lib/jenkins/.ssh/gplpriv'
//     def remoteHost = env.SSH_HOST_DL_RING_CX
//     def remoteHostOVH = env.DL_JAMI_OVH_NET
//     def remoteBaseDir = '/srv/repository/ring'
//     def ringPublicKeyFingerprint = 'A295D773307D25A33AE72F2F64CD5FA175348F84'
//     def snapcraft = '/var/lib/jenkins/.snap/key'

//     def topDir
//     def tarballsDir = '/opt/ring-contrib' // must exist on build node
//     def tarballsCacheExist = sh returnStatus: true, script: "test -d '${tarballsDir}'"
//     tarballsCacheExist = tarballsCacheExist == 0

//     def finalRepo = "";
//     if (env.CHANNEL == "nightly") {
//         finalRepo = "ring-nightly"
//     } else if (env.CHANNEL == "stable") {
//         finalRepo = "stable"
//     } else {
//         finalRepo = "ring-internal"
//     }

//     def finalManualRepo = "";
//     if (env.CHANNEL == "nightly") {
//         finalManualRepo = "ring-manual-nightly"
//     } else if (env.CHANNEL == "stable") {
//         finalManualRepo = "ring-manual"
//     } else {
//         finalManualRepo = "ring-manual-internal"
//     }

//     stage('SCM fetch') {
//         deleteDir()

//         sh """
//             git clone --depth=1 https://${RING_GERRIT_URL}/ring-project
//             cd ring-project
//             git fetch origin ${GERRIT_REFSPEC} && git checkout -q FETCH_HEAD
//             git log -n 1
//             git submodule update --init --recursive daemon lrc client-gnome
//         """

//         topDir = pwd() + '/ring-project'

//         // Install pre-fetched tarballs of libring dependencies
//         if (tarballsCacheExist) {
//             sh "cp ${tarballsDir}/* ${topDir}/daemon/contrib/tarballs/ || :"
//         }
//     }

//     dir (topDir) {
//         // Build date used inside the Qt client code
//         def clientBuildDate = sh returnStdout: true, script: "date -u '+%Y/%m/%d %H:%M:%S UTC'"
//         clientBuildDate = clientBuildDate.trim()


//         withEnv([   'RING_PACKAGING_IMAGE_SUFFIX=-deploy',
//                     "RING_CLIENT_BUILD_DATE='${clientBuildDate}'",
//                     'BATCH_MODE=1'
//             ]) {

//             stage('Build 32-bits') {
//                 if (env.DISTRIBUTION ==~ /ubuntu.*/ && env.DISTRIBUTION != "ubuntu_20.04" && env.DISTRIBUTION != "ubuntu_20.10") {
//                     docker.withRegistry('https://registry.hub.docker.com', 'hub.docker.com') {
//                         sh "make -f Makefile.packaging package-${DISTRIBUTION}_i386"
//                         if (env.BUILD_OCI == 'true') {
//                             sh "make -f Makefile.packaging package-${DISTRIBUTION}_i386_oci"
//                         }
//                     }
//                 } else {
//                     echo "32-bits build is not available on this platform"
//                 }
//             }

//             stage('Build 64-bits') {
//                 if (env.DISTRIBUTION ==~ /ubuntu.*/) {
//                     docker.withRegistry('https://registry.hub.docker.com', 'hub.docker.com') {
//                         sh "make -f Makefile.packaging package-${DISTRIBUTION}"
//                         if (env.BUILD_OCI == 'true') {
//                             sh "make -f Makefile.packaging package-${DISTRIBUTION}_oci"
//                         }
//                     }
//                 } else if (env.DISTRIBUTION ==~ /debian.*/) {
//                     docker.withRegistry('https://registry.hub.docker.com', 'hub.docker.com') {
//                         sh "make -f Makefile.packaging package-${DISTRIBUTION}"
//                         if (env.BUILD_OCI == 'true') {
//                             sh "make -f Makefile.packaging package-${DISTRIBUTION}_oci"
//                         }
//                     }
//                 } else if (env.DISTRIBUTION ==~ /raspbian.*/) {
//                     echo "x86-64 build is not available on this platform"
//                 } else {
//                     docker.withRegistry('https://registry.hub.docker.com', 'hub.docker.com') {
//                         sh "make -f Makefile.packaging package-${DISTRIBUTION}"
//                     }
//                 }
//             }

//             stage('Build armhf') {
//                 if (env.DISTRIBUTION ==~ /debian.*/) {
//                     //sh "make -f Makefile.packaging package-${DISTRIBUTION}_armhf"
//                     echo "armhf disabled on this platform until we optimize this build"
//                     if (env.BUILD_OCI == 'true') {
//                         //sh "make -f Makefile.packaging package-${DISTRIBUTION}_armhf_oci"
//                         echo "armhf disabled on this platform until we optimize this build"
//                     }
//                 } else if (env.DISTRIBUTION ==~ /raspbian.*/) {
//                     docker.withRegistry('https://registry.hub.docker.com', 'hub.docker.com') {
//                         sh "make -f Makefile.packaging package-${DISTRIBUTION}_armhf"
//                         if (env.BUILD_OCI == 'true') {
//                             sh "make -f Makefile.packaging package-${DISTRIBUTION}_armhf_oci"
//                         }
//                     }
//                 } else {
//                     echo "armhf build is not available on this platform"
//                 }
//             }

//             stage('Build arm64') {
//                 if (env.DISTRIBUTION ==~ /debian.*/) {
//                     //sh "make -f Makefile.packaging package-${DISTRIBUTION}_arm64"
//                     echo "arm64 disabled on this platform until we optimize this build"
//                     if (env.BUILD_OCI == 'true') {
//                         //sh "make -f Makefile.packaging package-${DISTRIBUTION}_arm64_oci"
//                         echo "arm64 disabled on this platform until we optimize this build"
//                     }
//                 } else {
//                     echo "arm64 build is not available on this platform"
//                 }
//             }
//         }

//         stage('Deploy') {
//             sh """export RSYNC_RSH='ssh -i ${sshPrivateKey}'
//             scripts/deploy-packages.sh \
//             --distribution=${DISTRIBUTION} \
//             --keyid="${ringPublicKeyFingerprint}" \
//             --snapcraft-login="${snapcraft}" \
//             --remote-repository-location="${remoteHost}:${remoteBaseDir}/${finalRepo}" \
//             --remote-manual-download-location="${remoteHost}:${remoteBaseDir}/${finalManualRepo}"
//             """
//         }
//     }
// }
