# check input
# exports all variables, to be used by scripts

STEABHW="petalinux-image-minimal"
CONFIG=""
package=${0}

CONFDIR="$(realpath $(dirname $0))/../sources/meta-steab/conf"

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - build selector"
      echo " "
      echo "$package [options] [arguments]"
      echo " "
      echo "options:"
      echo "-h, --help                	show brief help"
      echo "-b, --base=variant       specify which base image to build, valid iamges are ... k26.."
      echo "-d, --debug      		        specify if debug should be enabled"
      exit 0
      ;;
    -d| --debug)
	    CONFIG+=" -r ${CONFDIR}/debug_build.cfg"
      shift
      ;;
    -b*| --base*)
      shift
      if test $# -gt 0; then
        export STEABHW=$1
      else
        echo "no variant specified, using ${STEABHW}"
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done

export CONFIG="${CONFIG}"
export STEABHW="${STEABHW}"
export BB_ENV_PASSTHROUGH_ADDITIONS="BB_ENV_PASSTHROUGH_ADDITIONS:STEABHW:CONFIG"