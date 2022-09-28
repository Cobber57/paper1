<?php

/**

 * The base configuration for WordPress

 *

 * The wp-config.php creation script uses this file during the installation.

 * You don't have to use the web site, you can copy this file to "wp-config.php"

 * and fill in the values.

 *

 * This file contains the following configurations:

 *

 * * MySQL settings

 * * Secret keys

 * * Database table prefix

 * * ABSPATH

 *

 * @link https://wordpress.org/support/article/editing-wp-config-php/

 *

 * @package WordPress

 */


// ** MySQL settings - You can get this info from your web host ** //

/** The name of the database for WordPress */

define( 'DB_NAME', 'bitnami_wordpress' );
define( 'IMPORT_DEBUG', true );

/** MySQL database username */

define( 'DB_USER', 'bn_wordpress' );


/** MySQL database password */

define( 'DB_PASSWORD', '48c91eb35eebe9d14501deca7f2d5b1e0a188dfbbbf63fcf8a5b4a9cceafc8fb' );


/** MySQL hostname */

define( 'DB_HOST', 'localhost:3306' );


/** Database charset to use in creating database tables. */

define( 'DB_CHARSET', 'utf8' );


/** The database collate type. Don't change this if in doubt. */

define( 'DB_COLLATE', '' );


/**#@+

 * Authentication unique keys and salts.

 *

 * Change these to different unique phrases! You can generate these using

 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.

 *

 * You can change these at any point in time to invalidate all existing cookies.

 * This will force all users to have to log in again.

 *

 * @since 2.6.0

 */

define( 'AUTH_KEY',         'J-pZ2Q{CG(8yM$zuew^qX,2vw0H9]A,akROk+ivF.Q_<*/^fp2`,,~OgD^Ifr_|n' );

define( 'SECURE_AUTH_KEY',  '$tu<jy*7kn >8-e/EcR =[(IL?92*O@8x`~Amd]{40{(8rGeQE,W^D~QH`5AS^FE' );

define( 'LOGGED_IN_KEY',    'I/)X2Jdy;c59H*D?}bpCm:N]9f8Sx]%s}*`sq?MX!hV}G+Q`PYC!}^]?4-4%ZkD/' );

define( 'NONCE_KEY',        '!G0uz)=QOKw3Gp<bpoZ+gv/$5BaAAWW%pFo%:RN&Uh6k&L`rH=D8v${t#<|mbK~l' );

define( 'AUTH_SALT',        '>nA)^uurz*r5<<ylk@PefoNQ;(Ts0{aRA--qgAhX`1Kj{[t-)?di~%k6a{jps?K`' );

define( 'SECURE_AUTH_SALT', '1)93q5Xnewy<a_l{ 9llt%1c`/ZxuM6%HJ.j21;c,<_eXFIvJiJ.)eOt=OE&7~pn' );

define( 'LOGGED_IN_SALT',   'U;sY}(K#kNS`sek,dG?BK6C,#d<T5k[kus!i4UCo(# uoiK/f+Qw3{aF>~e#]qe~' );

define( 'NONCE_SALT',       'TKmWoxc<O4VZYY8nG.~|y~UP0G&(H]Dl.RchzEvon@I:fiuz.WkQGG>{]GNr[/ns' );


/**#@-*/


/**

 * WordPress database table prefix.

 *

 * You can have multiple installations in one database if you give each

 * a unique prefix. Only numbers, letters, and underscores please!

 */

$table_prefix = 'wp_';


/**

 * For developers: WordPress debugging mode.

 *

 * Change this to true to enable the display of notices during development.

 * It is strongly recommended that plugin and theme developers use WP_DEBUG

 * in their development environments.

 *

 * For information on other constants that can be used for debugging,

 * visit the documentation.

 *

 * @link https://wordpress.org/support/article/debugging-in-wordpress/

 */

define( 'WP_DEBUG', false );


/* Add any custom values between this line and the "stop editing" line. */




define( 'FS_METHOD', 'direct' );
/**
 * The WP_SITEURL and WP_HOME options are configured to access from any hostname or IP address.
 * If you want to access only from an specific domain, you can modify them. For example:
 *  define('WP_HOME','http://example.com');
 *  define('WP_SITEURL','http://example.com');
 *
 */
if ( defined( 'WP_CLI' ) ) {
	$_SERVER['HTTP_HOST'] = '127.0.0.1';
}

define( 'WP_HOME', 'http://' . $_SERVER['HTTP_HOST'] . '/' );
define( 'WP_SITEURL', 'http://' . $_SERVER['HTTP_HOST'] . '/' );
define( 'WP_AUTO_UPDATE_CORE', 'minor' );
/* That's all, stop editing! Happy publishing. */


/** Absolute path to the WordPress directory. */

if ( ! defined( 'ABSPATH' ) ) {

	define( 'ABSPATH', __DIR__ . '/' );

}


/** Sets up WordPress vars and included files. */

require_once ABSPATH . 'wp-settings.php';

/**
 * Disable pingback.ping xmlrpc method to prevent WordPress from participating in DDoS attacks
 * More info at: https://docs.bitnami.com/general/apps/wordpress/troubleshooting/xmlrpc-and-pingback/
 */
if ( !defined( 'WP_CLI' ) ) {
	// remove x-pingback HTTP header
	add_filter("wp_headers", function($headers) {
		unset($headers["X-Pingback"]);
		return $headers;
	});
	// disable pingbacks
	add_filter( "xmlrpc_methods", function( $methods ) {
		unset( $methods["pingback.ping"] );
		return $methods;
	});
}
