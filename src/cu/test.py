from argparse import ArgumentParser
from logging import basicConfig, getLogger, DEBUG, INFO
from os import symlink, unlink
from os.path import join, islink, isdir
from subprocess import check_call

from . import UPLOAD_DIR, all_uids, all_timestamps
from .testrunner import TestRunner, isots, rmrotree

LOG_LEVEL = INFO
basicConfig( format = '%(asctime)s %(levelname)s: [%(funcName)s] %(message)s', datefmt = '%Y-%m-%d %H:%M:%S', level = LOG_LEVEL )
LOGGER = getLogger( __name__ )

def run( uid, timestamp = None, result_dir = None, clean = None ):
	if not result_dir: result_dir = UPLOAD_DIR
	if not timestamp: timestamp = max( all_timestamps( uid ) )
	dest_dir = join( result_dir, uid, timestamp )
	if isdir( dest_dir ):
		if clean: rmrotree( dest_dir )
		else:
			LOGGER.info( 'Test for uid {2}, skipped ({0} already exists, corresponding to time {1})'.format( dest_dir, isots( timestamp ), uid ) )
			return
	with TestRunner( uid, timestamp ) as tr:
		tr.toxml()
		tr.saveto( dest_dir )
		tr_as_str = str( tr )
	latest = join( result_dir, uid, 'latest' )
	if islink( latest ): unlink( latest )
	symlink( timestamp, latest )
	LOGGER.info( 'Test for uid {2}, saved in {0} by {1}'.format( dest_dir, tr_as_str, uid ) )

def build( jenkins_workspace, jenkins_cli, uid, timestamp = None ):
	if not timestamp: timestamp = max( all_timestamps( uid ) )
	dest_dir = join( jenkins_workspace, uid, uid, timestamp )
	if isdir( dest_dir ):
		LOGGER.info( 'Test for uid {1}, skipped (time {0})'.format( isots( timestamp ), uid ) )
		return
	cmd = [ jenkins_cli, 'build', uid, '-p', 'timestamp={0}'.format( timestamp ), '-p', 'uid={0}'.format( uid ) ]
	print ' '.join( cmd )
	check_call( cmd )
	LOGGER.info( 'Test for uid {1}, scheduled (time {0})'.format( isots( timestamp ), uid ) )

def main():

	parser = ArgumentParser( prog = 'cu test' )
	parser.add_argument( '--jenkins_cli', '-j', help = 'If defined to the local Jenkins cli script, it will be used to issue builds (instead of running them locally)' )
	parser.add_argument( '--uid', '-u', help = 'The UID to test (default: all)' )
	parser.add_argument( '--results_dir', '-r', help = 'The destination directory where to store the results (default: UPLOAD_DIR)' )
	parser.add_argument( '--timestamp', '-t', help = 'The timestamp of the upload to test (default: latest)' )
	parser.add_argument( '--clean', '-c', action='store_true', help = 'Whether to clean the destination result directory first' )
	args = parser.parse_args()

	if args.jenkins_cli:
		for uid in [ args.uid ] if args.uid else all_uids():
			build( args.results_dir, args.jenkins_cli, uid, args.timestamp )
	else:
		for uid in [ args.uid ] if args.uid else all_uids():
			run( uid, args.timestamp, args.results_dir, args.clean )
