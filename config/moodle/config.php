<?php  // Moodle configuration file

unset($CFG);
global $CFG;
$CFG = new stdClass();

$CFG->dbtype    = 'mysqli';
$CFG->dblibrary = 'native';
$CFG->dbhost    = 'mysql';
$CFG->dbname    = getenv('MOODLE_DATABASE_NAME');
$CFG->dbuser    = getenv('MOODLE_DATABASE_USER');;
$CFG->dbpass    = getenv('MOODLE_DATABASE_PASSWORD'); ;
$CFG->prefix    = 'mdl_';
$CFG->dboptions = array (
  'dbpersist' => 0,
  'dbport' => '',
  'dbsocket' => '',
  'dbcollation' => 'utf8mb4_bin',
);

$CFG->wwwroot              = 'http://localhost:8080';
$CFG->dataroot             = '/var/www/moodledata';
$CFG->admin                = 'admin';

$CFG->directorypermissions = 0777;
$CFG->smtphosts            = 'mailpit:1025';
$CFG->noreplyaddress       = 'noreply@example.com';

$CFG->debug                = (E_ALL | E_STRICT);
$CFG->cronclionly          = 0;

require_once(__DIR__ . '/lib/setup.php');

// There is no php closing tag in this file,
// it is intentional because it prevents trailing whitespace problems!
