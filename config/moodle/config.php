<?php  // Moodle configuration file

unset($CFG);
global $CFG;
$CFG = new stdClass();

$CFG->dbtype    = 'mysqli';
$CFG->dblibrary = 'native';
$CFG->dbhost    = 'mysql';
$CFG->dbname    = getenv('MOODLE_DATABASE_NAME');
$CFG->dbuser    = getenv('MOODLE_DATABASE_USER');
$CFG->dbpass    = getenv('MOODLE_DATABASE_PASSWORD');
$CFG->prefix    = 'mdl_';
$CFG->dboptions = array (
  'dbpersist' => 0,
  'dbport' => '',
  'dbsocket' => '',
  'dbcollation' => 'utf8mb4_bin',
);

if ($_SERVER['HTTP_HOST'] == 'localhost:' . getenv('MOODLE_APACHE_PORT'))
{
  $CFG->wwwroot            = 'http://localhost:' . getenv('MOODLE_APACHE_PORT');
} else {
  $CFG->wwwroot            = 'http://moodle';
}

$CFG->dataroot             = '/var/www/moodledata';
$CFG->admin                = 'admin';

$CFG->directorypermissions = 0777;
$CFG->smtphosts            = 'mailpit:1025';
$CFG->noreplyaddress       = 'noreply@example.com';

$CFG->debug                    = (E_ALL | E_STRICT);
$CFG->cronclionly              = 0;
$CFG->curlsecurityblockedhosts = "127.0.0.1";
// $CFG->reverseproxy             = 1;
$CFG->enablewebservices        = 1;
$CFG->enablewsdocumentation    = 1;
$CFG->webserviceprotocols      = "rest";

$CFG->forced_plugin_settings['logstore_xapi'] = [
  'backgroundmode' => 0,
  'endpoint' => getenv('HOOK_RALPH_URL') . '/xAPI/statements',
  'username' => getenv('HOOK_RALPH_LRS_AUTH_USER_NAME'),
  'password' => getenv('HOOK_RALPH_LRS_AUTH_USER_PASSWORD'),
];
$CFG->forced_plugin_settings['tool_log']['enabled_stores'] = 'logstore_standard,logstore_xapi';

require_once(__DIR__ . '/lib/setup.php');

// There is no php closing tag in this file,
// it is intentional because it prevents trailing whitespace problems!
