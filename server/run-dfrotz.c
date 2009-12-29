#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <memory.h>
#include <errno.h>
#include <pwd.h>

#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>

#include <netinet/in.h>

#include <linux/capability.h>

int no_fork;


void
usage (void)
{
	fprintf (stderr, "usage: run-dfrotz\n");
	exit (1);
}

char *conf_key;
char *zfile_name;

char *pipe_name_tofrotz;
char *pipe_name_fromfrotz;

int tofrotz_fd;
int fromfrotz_fd;

char aux_dir[1000];
char z5_filename[1000];

char cmd_name[1000];

int port;

int fds_to_frotz[2];
int fds_from_frotz[2];

int to_frotz, from_frotz;

int listen_sock;
int client_sock;

int pid;

int use_logfile;

char log_name[1000];

int orig_stdout;
int log_fd;

double
get_secs (void)
{
	struct timeval tv;
	gettimeofday (&tv, NULL);
	return (tv.tv_sec + tv.tv_usec / 1e6);
}

double base_secs;

char *game_dir;

void
chroot_link (char *from_name, char *to_name)
{
	if (link (from_name, to_name) < 0) {
		fprintf (stderr, "error linking %s to %s\n",
			 from_name, to_name);
		exit (1);
	}
}

void
setup_chroot (void)
{
	char from_name[1000];
	char to_name[1000];

	if (mkdir (game_dir, 0755) < 0) {
		printf ("error: mkdir %s\n", game_dir);
		exit (1);
	}

	sprintf (from_name, "%s/bin/dfrotz", aux_dir);
	sprintf (to_name, "%s/dfrotz", game_dir);
	chroot_link (from_name, to_name);

	sprintf (from_name, "%s/z5/%s.z5", aux_dir, zfile_name);
	sprintf (to_name, "%s/game.z5", game_dir);
	chroot_link (from_name, to_name);

	seteuid (0);
	if (chroot (game_dir) < 0) {
		printf ("error doing chroot %s: redo install-dev\n", game_dir);
		if (no_fork == 0) {
			exit (1);
		} else {
			chdir (game_dir);
		}
	} else {
		if (chdir ("/") < 0) {
			printf ("chdir failed\n");
			exit (1);
		}
		printf ("chdir ok\n");

	}

	setuid (getuid ());

	sprintf (cmd_name, "./dfrotz");
	sprintf (z5_filename, "game.z5");
}

char argbuf[1000];

int
main (int argc, char **argv)
{
	int c;
	int ac;
	char *av[100];
	int fd;
	struct sockaddr_in addr;
	socklen_t addrlen;
	fd_set rset;
	int maxfd;
	int n;
	char buf[1000];
	struct timeval tv;
	double now;
	char *outp;
	int i;

	seteuid (getuid ());

	outp = argbuf;
	for (i = 0; i < argc; i++) {
		sprintf (outp, "%s ", argv[i]);
		outp += strlen (outp);
	}

	setbuf (stdout, NULL);
	setbuf (stderr, NULL);

	fd = open ("/dev/null", O_RDONLY);
	dup2 (fd, 0);
	close (fd);

	for (fd = 3; fd < 100; fd++)
		close (fd);

	while ((c = getopt (argc, argv, "k:Ld:n")) != EOF) {
		switch (c) {
		case 'n':
			no_fork = 1;
			break;
		case 'd':
			game_dir = optarg;
			break;
		case 'L':
			use_logfile = 1;
			break;
		case 'k':
			conf_key = optarg;
			break;
		default:
			usage ();
		}
	}

	if (optind >= argc)
		usage ();
	
	zfile_name = argv[optind++];

	if (optind != argc)
		usage ();

	if (strlen (zfile_name) > 30) {
		fprintf (stderr, "invalid zfile name\n");
		exit (1);
	}

	if (conf_key == NULL) {
		struct passwd *pw;

		if ((pw = getpwuid (getuid ())) == NULL) {
			fprintf (stderr, "can't get my name\n");
			exit (1);
		}

		conf_key = malloc (100);
		sprintf (conf_key, "%s-dev", pw->pw_name);
	}
			
	if (strlen (conf_key) > 50) {
		fprintf (stderr, "invalid conf_key\n");
		exit (1);
	}

	sprintf (aux_dir, "/var/zorky-%s", conf_key);

	orig_stdout = dup (1);

	if (use_logfile) {
		sprintf (log_name, "%s/tmp/dfrotz.log", aux_dir);
		log_fd = open (log_name,
			   O_WRONLY | O_CREAT | O_APPEND, 0666);
		if (log_fd < 0) {
			fprintf (stderr, "can't create log file\n");
			exit (1);
		}
		fchmod (log_fd, 0666);
		dup2 (log_fd, 1);
		dup2 (log_fd, 2);
	}

	printf ("\n");
	printf ("running: %s\n", argbuf);

	listen_sock = socket (AF_INET, SOCK_STREAM, 0);
	listen (listen_sock, 1);

	addrlen = sizeof addr;
	if (getsockname (listen_sock, (struct sockaddr *)&addr, &addrlen) < 0) {
		perror ("getsockname");
		exit (1);
	}

	port = ntohs (addr.sin_port);

	printf ("startp id %d\n", getpid ());
	printf ("port = %d\n", port);

	if (game_dir == NULL) {
		printf ("game_dir must be specified\n");
		exit (1);
	}

	setup_chroot ();

	if (no_fork) {
		pid = 0;
	} else {
		if ((pid = fork ()) < 0) {
			fprintf (stderr, "fork error\n");
			exit (1);
		}
	}

	if (pid > 0) {
		printf ("child1 %d\n", pid);
		sprintf (buf, "%d %d\n", port, pid);
		write (orig_stdout, buf, strlen (buf));
		exit (0);
	}

	close (orig_stdout);

	ac = 0;
	av[ac++] = cmd_name;
	av[ac++] = z5_filename;
	av[ac] = NULL;

	if (pipe (fds_to_frotz) < 0
	    || pipe (fds_from_frotz) < 0) {
		fprintf (stderr, "error making pipes\n");
		exit (1);
	}

	printf ("ready to fork frotz\n");

	if (no_fork == 0) {
		if ((pid = fork ()) < 0) {
			fprintf (stderr, "fork error\n");
			exit (1);
		}
	} else {
		pid = 0;
	}

	if (pid == 0) {
		dup2 (fds_to_frotz[0], 0);
		dup2 (fds_from_frotz[1], 1);
		dup2 (1, 2);

		close (fds_to_frotz[0]);
		close (fds_to_frotz[1]);
		close (fds_from_frotz[0]);
		close (fds_from_frotz[1]);

		for (fd = 3; fd < 100; fd++) {
			if (fd != log_fd)
				close (fd);
		}

		sprintf (buf, "execing  %s %s %s %s %d %d\n",
			 cmd_name, av[0], av[1], av[2],
			 open (av[0],O_RDONLY),
			 open (av[1],O_RDONLY));
		write (log_fd, buf, strlen (buf));


		execv (cmd_name, av);
		
		sprintf (buf, "exec failed %s %s\n",
			 cmd_name, strerror (errno));
		write (log_fd, buf, strlen (buf));
		exit (1);
	}

	printf ("child2 %d\n", pid);

	to_frotz = fds_to_frotz[1];
	close (fds_to_frotz[0]);

	from_frotz = fds_from_frotz[0];
	close (fds_from_frotz[1]);

	fcntl (from_frotz, F_SETFL, O_NONBLOCK);

	base_secs = get_secs ();
	while (1) {
		FD_ZERO (&rset);

		maxfd = 0;

		FD_SET (listen_sock, &rset);
		if (listen_sock > maxfd)
			maxfd = listen_sock;

		tv.tv_sec = 1000;
		tv.tv_usec = 0;

		if (client_sock) {
			now = get_secs ();
			if (now - base_secs > .5) {
				fprintf (stderr, "frotz timeout\n");
				close (client_sock);
				client_sock = 0;
			}


			FD_SET (from_frotz, &rset);
			if (from_frotz > maxfd)
				maxfd = from_frotz;

			FD_SET (client_sock, &rset);
			if (client_sock > maxfd)
				maxfd = client_sock;

			tv.tv_sec = 0;
			tv.tv_usec = 50 * 1000;
		}

		if (select (maxfd + 1, &rset, NULL, NULL, &tv) < 0) {
			perror ("select");
			exit (1);
		}

		if (FD_ISSET (listen_sock, &rset)) {
			if ((fd = accept (listen_sock, NULL, NULL)) >= 0) {
				if (client_sock) {
					printf ("rejected second connection\n");
					close (fd);
				} else {
					printf ("connected...\n");
					client_sock = fd;
					fcntl (client_sock, F_SETFL,
					       O_NONBLOCK);
					base_secs = get_secs ();
				}
			}
		}

		if (client_sock) {
			if (FD_ISSET (from_frotz, &rset)) {
				errno = 0;
				n = read (from_frotz, buf, sizeof buf);
				if (n == 0
				    || (n < 0 && errno != EWOULDBLOCK)) {
					fprintf (stderr,
						 "frotz died %d %d\n",
						 n, errno);
					exit (0);
				} if (n > 0) {
					base_secs = get_secs ();
					write (client_sock, buf, n);
				}
			}

			if (FD_ISSET (client_sock, &rset)) {
				n = read (client_sock, buf, sizeof buf);
				if (n == 0
				    || (n < 0 && errno != EWOULDBLOCK)) {
					fprintf (stderr,
						 "client died\n");
					close (client_sock);
					client_sock = 0;
				} else {
					write (to_frotz, buf, n);
				}
			}
		}
	}

	return (0);
}

