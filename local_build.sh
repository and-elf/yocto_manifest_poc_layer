#!/bin/bash
thisdir=$(realpath $(dirname $0))

source ${thisdir}/../setupsdk
source ${thisdir}/handle_input.sh
echo ${BB_ENV_PASSTHROUGH_ADDITIONS}
bitbake ${STEABHW} ${CONFIG}