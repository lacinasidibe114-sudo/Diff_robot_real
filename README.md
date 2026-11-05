# Diff Robot Real

> **Workspace ROS 2 pour un robot mobile différentiel : simulation Gazebo et pilotage matériel réel**

`Diff_robot_real` est un workspace ROS 2 destiné à développer, simuler et piloter un robot mobile à deux roues motrices différentielles.

Le projet regroupe :

- une description robotique URDF/Xacro avec meshes ;
- une simulation Gazebo Fortress ;
- une interface matérielle `ros2_control` basée sur Arduino et liaison série ;
- un firmware Arduino pour deux moteurs DC avec encodeurs ;
- des régulateurs PID locaux pour les roues ;
- un `diff_drive_controller` pour convertir `/cmd_vel` en vitesses de roues ;
- une publication d'odométrie et de TF ;
- un driver Python optionnel pour MPU6050 ;
- des exemples de publishers, subscribers, services, paramètres et transformations TF ;
- des utilitaires de diagnostic de communication série.

> **Statut :** plateforme de développement et d'intégration robotique. Le mode matériel réel doit être testé roue levée, avec une limitation de courant et un arrêt d'urgence physique avant tout déplacement autonome.

## Sommaire

- [Objectifs](#objectifs)
- [Architecture](#architecture)
- [Modes d'exécution](#modes-dexécution)
- [Structure du workspace](#structure-du-workspace)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Compilation](#compilation)
- [Simulation Gazebo](#simulation-gazebo)
- [Pilotage du robot réel](#pilotage-du-robot-réel)
- [Interfaces ROS 2](#interfaces-ros-2)
- [Firmware Arduino](#firmware-arduino)
- [Contrôle différentiel](#contrôle-différentiel)
- [IMU MPU6050](#imu-mpu6050)
- [Description du robot et TF](#description-du-robot-et-tf)
- [Exemples ROS 2](#exemples-ros-2)
- [Dépannage](#dépannage)
- [Validation et tests](#validation-et-tests)
- [Limites connues](#limites-connues)
- [Sécurité](#sécurité)
- [Licence et contribution](#licence-et-contribution)

## Objectifs

Le workspace fournit une architecture commune pour passer progressivement :

```text
Développement ROS 2
        │
        ├── Visualisation URDF + RViz
        │
        ├── Simulation Gazebo + ros2_control
        │
        └── Robot réel + Arduino + moteurs + encodeurs
```

Le même modèle robotique et les mêmes contrôleurs peuvent être utilisés autant que possible dans les deux modes. Le choix du matériel est effectué dans le fichier Xacro via l'argument `is_sim`.

## Architecture

### Vue d'ensemble

```text
                                  ┌────────────────────────┐
                                  │        Utilisateur      │
                                  │ clavier / application   │
                                  └───────────┬────────────┘
                                              │ geometry_msgs/Twist
                                              ▼
                                  ┌────────────────────────┐
                                  │ /diff_drive_controller │
                                  │ cinématique différent. │
                                  └───────────┬────────────┘
                                              │ commandes roues
                         ┌────────────────────┴────────────────────┐
                         │                                         │
                         ▼                                         ▼
              ┌──────────────────────┐                 ┌──────────────────────┐
              │ Mode simulation      │                 │ Mode robot réel      │
              │ Ignition/Gazebo      │                 │ BumperbotInterface   │
              │ ign_ros2_control     │                 │ LibSerial + Arduino  │
              └──────────┬───────────┘                 └──────────┬───────────┘
                         │                                        │ USB série
                         ▼                                        ▼
              ┌──────────────────────┐                 ┌──────────────────────┐
              │ Physique Gazebo      │                 │ Firmware Arduino     │
              │ moteurs / roues      │                 │ PID + encodeurs      │
              └──────────┬───────────┘                 └──────────┬───────────┘
                         │                                        │
                         └────────────────┬───────────────────────┘
                                          ▼
                               ┌────────────────────────┐
                               │ États des roues        │
                               │ /joint_states          │
                               │ odom + TF               │
                               └────────────────────────┘
```

### Flux de commande

1. Une application publie un `geometry_msgs/msg/Twist` sur le topic du contrôleur différentiel.
2. `diff_drive_controller` calcule les vitesses de roue gauche et droite.
3. En simulation, `ign_ros2_control` transmet les commandes au modèle Gazebo.
4. En réel, `BumperbotInterface` convertit les vitesses en trame série.
5. L'Arduino applique un PID indépendant à chaque moteur.
6. Les encodeurs produisent les vitesses mesurées.
7. L'Arduino renvoie les états au PC.
8. ROS 2 met à jour les joints, l'odométrie et les transformations TF.

### Repères principaux

```text
odom
 └── base_footprint
      └── base_link
           ├── wheel_left_link
           ├── wheel_right_link
           ├── caster_front_link
           ├── caster_rear_link
           └── imu_link
```

## Modes d'exécution

### Mode simulation

Le mode simulation utilise :

- `ros_gz_sim` / Gazebo Fortress ;
- `ign_ros2_control/IgnitionSystem` ;
- le fichier `bumperbot_controllers.yaml` ;
- l'horloge `/clock` bridgée de Gazebo vers ROS 2 ;
- `use_sim_time: true`.

Il ne nécessite ni Arduino ni moteur physique.

### Mode robot réel

Le mode réel utilise :

- `bumperbot_firmware/BumperbotInterface` ;
- LibSerial ;
- un Arduino connecté en USB ;
- le firmware `robot_control.ino` ;
- le fichier `bumperbot_controllers_real.yaml` ;
- l'horloge système ;
- `use_sim_time: false`.

Le port série par défaut est `/dev/ttyUSB0`, à adapter à la machine.

### Visualisation seule

La visualisation ne démarre pas de moteur ni de contrôleur matériel. Elle utilise :

- `robot_state_publisher` ;
- `joint_state_publisher_gui` ;
- RViz 2 ;
- le fichier `rviz/display.rviz`.

## Structure du workspace

```text
Diff_robot_real/
├── README.md
├── LICENSE
├── src/
│   ├── arduino/                       # Exemples et nœuds série Python
│   ├── bas_example/                   # Exemples ROS 2 pédagogiques
│   ├── bumperbot_firmware/            # Interface matériel + firmware Arduino
│   ├── controller/                    # Contrôleurs et launch files
│   ├── robot_description/             # URDF, meshes, Gazebo et RViz
│   └── robot_msgs/                    # Services ROS 2 personnalisés
├── build/                             # Artefacts colcon générés
├── install/                           # Environnement ROS 2 généré
└── log/                               # Journaux de build et tests
```

### Rôle des packages

| Package | Rôle |
| --- | --- |
| `robot_description` | URDF/Xacro, meshes, paramètres Gazebo, RViz et launch de simulation |
| `bumperbot_firmware` | Plugin `ros2_control`, communication série, driver MPU6050 et exemples série |
| `controller` | Configuration des contrôleurs, cinématique différentielle et launch files |
| `robot_msgs` | Services `AddTwoInts` et `GetTransform` |
| `arduino` | Nœuds Python de démonstration et sketches Arduino |
| `bas_example` | Exemples de base pour ROS 2, paramètres, services, publishers, TF et subscriptions |

## Prérequis

### Logiciels

- Ubuntu compatible avec votre distribution ROS 2 ;
- ROS 2 Humble ou distribution compatible avec Gazebo Fortress ;
- `colcon` et `rosdep` ;
- Python 3 ;
- compilateur C++ ;
- Arduino IDE ou Arduino CLI ;
- Gazebo Fortress / `ros_gz_sim` ;
- RViz 2.

### Matériel pour le robot réel

- châssis différentiel ;
- deux moteurs DC avec encodeurs ;
- deux ponts de puissance ou un driver double compatible ;
- Arduino compatible avec les interruptions utilisées ;
- alimentation moteur séparée ;
- câble USB de données ;
- arrêt d'urgence ou coupure de puissance ;
- capteur MPU6050 optionnel.

### Dépendances ROS 2

Installation indicative :

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  pkg-config \
  libserial-dev \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-pip \
  ros-$ROS_DISTRO-ros2-control \
  ros-$ROS_DISTRO-ros2-controllers \
  ros-$ROS_DISTRO-controller-manager \
  ros-$ROS_DISTRO-diff-drive-controller \
  ros-$ROS_DISTRO-joint-state-broadcaster \
  ros-$ROS_DISTRO-velocity-controllers \
  ros-$ROS_DISTRO-robot-state-publisher \
  ros-$ROS_DISTRO-joint-state-publisher-gui \
  ros-$ROS_DISTRO-rviz2 \
  ros-$ROS_DISTRO-xacro \
  ros-$ROS_DISTRO-ros-gz-sim \
  ros-$ROS_DISTRO-ros-gz-bridge \
  ros-$ROS_DISTRO-teleop-twist-keyboard
```

Pour le driver MPU6050 et les utilitaires série Python :

```bash
python3 -m pip install pyserial smbus
```

Selon la distribution, `smbus` peut être fourni de préférence par le système :

```bash
sudo apt install -y python3-smbus python3-serial
```

## Installation

### 1. Créer le workspace

```bash
mkdir -p ~/diff_robot_ws/src
cd ~/diff_robot_ws/src
git clone https://github.com/lacinasidibe114-sudo/Diff_robot_real.git
cd ~/diff_robot_ws
```

### 2. Initialiser ROS 2 et rosdep

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 3. Compiler

```bash
cd ~/diff_robot_ws
colcon build --symlink-install
source install/setup.bash
```

Pour charger automatiquement le workspace :

```bash
echo "source ~/diff_robot_ws/install/setup.bash" >> ~/.bashrc
```

## Compilation

Compilation complète :

```bash
cd ~/diff_robot_ws
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Compilation d'un package :

```bash
colcon build --symlink-install \
  --packages-select robot_description bumperbot_firmware controller robot_msgs
```

Recompiler avec les dépendances en amont :

```bash
colcon build --symlink-install \
  --packages-up-to controller
```

Vérifier que les packages sont visibles :

```bash
ros2 pkg list | grep -E 'robot_description|bumperbot_firmware|controller|robot_msgs'
```

> Les répertoires `build/`, `install/` et `log/` sont générés par Colcon. Ils ne doivent pas être utilisés comme source de configuration ; les fichiers de référence se trouvent sous `src/`.

## Simulation Gazebo

### Lancer la simulation minimale

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/diff_robot_ws/install/setup.bash
ros2 launch robot_description gazebo.launch.py
```

Cette commande :

1. génère l'URDF depuis `robot.urdf.xacro` ;
2. lance `robot_state_publisher` ;
3. démarre Gazebo Fortress ;
4. configure `GZ_SIM_RESOURCE_PATH` pour les meshes ;
5. insère le robot depuis `/robot_description` ;
6. bridge `/clock` vers ROS 2 ;
7. charge `joint_state_broadcaster` ;
8. charge `diff_drive_controller`.

### Lancer simulation avec téléop clavier

```bash
ros2 launch robot_description gazebo_complet.launch.py
```

La téléopération est activée par défaut via un terminal `xterm`. Installer `xterm` si nécessaire :

```bash
sudo apt install -y xterm
```

Désactiver la téléopération :

```bash
ros2 launch robot_description gazebo_complet.launch.py use_teleop:=false
```

Le nœud de téléopération redirige `/cmd_vel` vers :

```text
/diff_drive_controller/cmd_vel_unstamped
```

### Lancer avec un modèle différent

```bash
ros2 launch robot_description gazebo.launch.py \
  model:=/chemin/absolu/vers/robot.urdf.xacro
```

### Contrôler la simulation manuellement

```bash
ros2 topic pub --once \
  /diff_drive_controller/cmd_vel_unstamped \
  geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.0}}"
```

Arrêt :

```bash
ros2 topic pub --once \
  /diff_drive_controller/cmd_vel_unstamped \
  geometry_msgs/msg/Twist \
  "{}"
```

Observer l'odométrie :

```bash
ros2 topic echo /diff_drive_controller/odom
```

## Pilotage du robot réel

### 1. Préparer l'Arduino

Le firmware principal est :

```text
src/bumperbot_firmware/firmware/robot_control/robot_control.ino
```

Installer la bibliothèque Arduino `PID_v1`, sélectionner la carte, puis téléverser le sketch.

### 2. Configurer le port série

Le fichier `src/robot_description/urdf/bumperbot_ros2_control.xacro` utilise actuellement :

```xml
<param name="port">/dev/ttyUSB0</param>
```

Identifier le port :

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Pour une identification stable :

```bash
ls -l /dev/serial/by-id/
```

Ajouter l'utilisateur au groupe série :

```bash
sudo usermod -aG dialout "$USER"
```

Reconnectez-vous ensuite à la session.

### 3. Vérifier la connexion série

```bash
stty -F /dev/ttyUSB0 115200 cs8 -cstopb -parenb
cat /dev/ttyUSB0
```

Fermez Arduino Serial Monitor avant de démarrer ROS 2. L'ouverture du port série redémarre généralement l'Arduino via DTR ; l'interface attend 2,5 secondes et vide les buffers avant de commencer.

### 4. Lancer le robot réel

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/diff_robot_ws/install/setup.bash
ros2 launch controller real_robot.launch.py
```

Le launch réel :

1. génère l'URDF avec `is_sim:=False` ;
2. lance `robot_state_publisher` avec l'horloge système ;
3. démarre `ros2_control_node` ;
4. charge `bumperbot_controllers_real.yaml` ;
5. démarre `joint_state_broadcaster` ;
6. démarre `diff_drive_controller`.

### 5. Commander le robot réel

Le contrôleur réel utilise une commande non estampillée :

```bash
ros2 topic pub --rate 10 \
  /diff_drive_controller/cmd_vel_unstamped \
  geometry_msgs/msg/Twist \
  "{linear: {x: 0.1}, angular: {z: 0.0}}"
```

Arrêter immédiatement :

```bash
ros2 topic pub --once \
  /diff_drive_controller/cmd_vel_unstamped \
  geometry_msgs/msg/Twist \
  "{}"
```

Le timeout de commande est configuré à `0.5 s`. Si aucune nouvelle commande n'arrive, le contrôleur doit ramener la commande à zéro.

## Interfaces ROS 2

### Topics principaux

| Topic | Type | Rôle |
| --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | commande utilisée par le contrôleur personnalisé |
| `/diff_drive_controller/cmd_vel_unstamped` | `geometry_msgs/msg/Twist` | commande du contrôleur différentiel |
| `/diff_drive_controller/odom` | `nav_msgs/msg/Odometry` | odométrie du robot |
| `/joint_states` | `sensor_msgs/msg/JointState` | états des joints |
| `/tf` | `tf2_msgs/msg/TFMessage` | transformations dynamiques |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | transformations fixes |
| `/imu/out` | `sensor_msgs/msg/Imu` | mesures du MPU6050 optionnel |
| `/serial_receiver` | `std_msgs/msg/String` | données série reçues par l'utilitaire Python |
| `/serial_transmitter` | `std_msgs/msg/String` | commandes série de l'utilitaire Python |

### Contrôleurs

Simulation et robot réel utilisent :

```text
diff_drive_controller
joint_state_broadcaster
```

Le package `controller` contient également :

```text
simple_velocity_controller
```

utilisé avec `simple_controller.py` pour convertir manuellement `/cmd_vel` en vitesses de roues.

Lister l'état des contrôleurs :

```bash
ros2 control list_controllers
```

Lister les interfaces :

```bash
ros2 control list_hardware_interfaces
```

### Services personnalisés

`robot_msgs` génère :

#### `robot_msgs/srv/AddTwoInts`

```text
int64 a
int64 b
---
int64 sum
```

#### `robot_msgs/srv/GetTransform`

```text
string frame_id
string child_frame_id
---
geometry_msgs/TransformStamped transform
bool success
```

## Firmware Arduino

### Brochage principal

Le sketch `robot_control.ino` utilise :

| Fonction | Arduino |
| --- | --- |
| PWM moteur droit | D9 |
| PWM moteur gauche | D11 |
| Direction moteur droit | D12 / D13 |
| Direction moteur gauche | D7 / D8 |
| Encodeur droit phase A | D3 |
| Encodeur droit phase B | D5 |
| Encodeur gauche phase A | D2 |
| Encodeur gauche phase B | D4 |
| Série | USB, 115200 bauds |

### Boucle de contrôle

Le firmware :

- lit les commandes série caractère par caractère ;
- distingue les commandes `r` et `l` ;
- interprète `p` comme direction positive et `n` comme négative ;
- calcule la vitesse toutes les 100 ms ;
- exécute un PID séparé pour chaque roue ;
- applique le PWM via le L298N ;
- renvoie les vitesses mesurées.

Gains actuels :

| Roue | Kp | Ki | Kd |
| --- | ---: | ---: | ---: |
| Droite | 11.5 | 7.5 | 0.1 |
| Gauche | 12.8 | 8.3 | 0.1 |

### Variantes firmware

Le dépôt contient notamment :

| Fichier | Usage |
| --- | --- |
| `robot_control.ino` | firmware principal |
| `robot_control_inverted.ino` | variante avec broches/directions inversées |
| `simple_encoder_reader.ino` | test de lecture des encodeurs |
| `simple_motor_control.ino` | test de commande moteur |
| `simple_serial_receiver.ino` | test de réception série |
| `simple_serial_transmitter.ino` | test d'émission série |

Choisissez une seule variante correspondant au câblage réel.

## Protocole série

### PC → Arduino

Le plugin envoie une commande de la forme :

```text
rp<right_velocity>,lp<left_velocity>,
```

ou, pour les vitesses négatives :

```text
rn<right_velocity>,ln<left_velocity>,
```

Exemple :

```text
rp01.50,ln02.00,
```

La convention actuelle est :

```text
r = roue droite
l = roue gauche
p = direction positive
n = direction négative
```

L'ordre des joints dans le Xacro réel est important :

```text
index 0 = wheel_right_joint
index 1 = wheel_left_joint
```

### Arduino → PC

Le firmware renvoie :

```text
rp<right_velocity>,lp<left_velocity>,
```

Exemple :

```text
rp1.25,ln1.18,
```

Le plugin interprète :

- le premier caractère comme la roue ;
- le deuxième caractère comme le signe ;
- la valeur restante comme une vitesse ;
- puis intègre la vitesse dans le temps pour estimer la position.

### Paramètres série

| Paramètre | Valeur |
| --- | --- |
| Débit | `115200` |
| Format | `8N1` |
| Contrôle de flux | aucun |
| Période firmware | `100 ms` |
| Timeout contrôleur | `0.5 s` |

## Contrôle différentiel

### Modèle cinématique

Pour un robot différentiel :

```text
v_left  = (v - ω × L / 2) / R
v_right = (v + ω × L / 2) / R
```

où :

- `v` est la vitesse linéaire en m/s ;
- `ω` est la vitesse angulaire en rad/s ;
- `L` est la séparation entre les roues ;
- `R` est le rayon des roues.

Les paramètres principaux configurés sont :

| Paramètre | Simulation | Réel |
| --- | ---: | ---: |
| Rayon roue | `0.033 m` | `0.033 m`, à mesurer |
| Séparation roues | `0.14 m` | `0.14 m`, à mesurer |
| Fréquence contrôleur | `100 Hz` | `100 Hz` |
| Publication odométrie | `50 Hz` | `50 Hz` |
| Timeout commande | `0.5 s` | `0.5 s` |

Le fichier `controller_cinematique.launch.py` utilise par défaut une séparation de `0.17 m` pour le contrôleur personnalisé. Cette valeur doit être harmonisée avec la géométrie réelle avant une utilisation précise.

### Contrôleur personnalisé

`src/controller/simple_controller.py` :

- s'abonne à `/cmd_vel` ;
- utilise `wheel_radius` et `wheel_separation` ;
- publie sur `/simple_velocity_controller/commands` ;
- publie les vitesses dans l'ordre `[roue droite, roue gauche]`.

Lancer ce mode :

```bash
ros2 launch controller controller_cinematique.launch.py
```

Avec des dimensions personnalisées :

```bash
ros2 launch controller controller_cinematique.launch.py \
  wheel_radius:=0.033 \
  wheel_separation:=0.14
```

## IMU MPU6050

Le driver Python `bumperbot_firmware/mpu6050_driver.py` lit directement le MPU6050 sur I2C et publie :

```text
/imu/out
sensor_msgs/msg/Imu
```

Paramètres matériels utilisés dans le code :

| Élément | Valeur |
| --- | --- |
| Adresse I2C | `0x68` |
| Bus Linux | `1` |
| Fréquence de publication | `100 Hz` |
| Frame | `base_footprint` |

Lancer le driver :

```bash
ros2 run bumperbot_firmware mpu6050_driver.py
```

Vérifier les données :

```bash
ros2 topic echo /imu/out
ros2 topic hz /imu/out
```

Le driver réinitialise la connexion I2C après une erreur `OSError`. Vérifiez l'alimentation, les lignes SDA/SCL et l'adresse du module.

> Les facteurs de conversion présents dans le driver doivent être vérifiés expérimentalement pour la configuration réelle du MPU6050. Les covariances du message IMU ne sont pas configurées dans le code actuel.

## Description du robot et TF

### URDF/Xacro

Le fichier principal est :

```text
src/robot_description/urdf/robot.urdf.xacro
```

Il décrit :

- `base_footprint` ;
- `base_link` ;
- les roues gauche et droite ;
- les roulettes avant et arrière ;
- `imu_link` ;
- les joints continus des roues ;
- les meshes STL ;
- l'intégration Gazebo ;
- le bloc `ros2_control`.

### Visualiser le robot dans RViz

```bash
ros2 launch robot_description display.launch.py
```

Cette commande lance :

- `robot_state_publisher` ;
- `joint_state_publisher_gui` ;
- RViz avec `rviz/display.rviz`.

### Vérifier l'arbre TF

```bash
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom base_footprint
```

## Exemples ROS 2

Le package `bas_example` contient des exemples d'apprentissage :

| Fichier | Fonction |
| --- | --- |
| `simple_publisher.py` | publisher simple |
| `simple_subscriber.py` | subscriber simple |
| `simple_parameter.py` | paramètres ROS 2 |
| `simple_service_server.py` | serveur de service |
| `simple_service_client.py` | client de service |
| `simple_lifecycle_node.py` | nœud lifecycle |
| `simple_tf_kinematics.py` | publication TF |
| `simple_tf_kinematics_request.py` | requête de transformation |

Les utilitaires série Python du package `arduino` permettent de tester un port indépendamment du plugin C++ :

```bash
ros2 run arduino simple_serial_receiver \
  --ros-args -p port:=/dev/ttyUSB0 -p baudrate:=115200
```

```bash
ros2 run arduino simple_serial_transmitter \
  --ros-args -p port:=/dev/ttyUSB0 -p baudrate:=115200
```

## Dépannage

### Gazebo ne trouve pas les meshes

Vérifier :

```bash
echo "$GZ_SIM_RESOURCE_PATH"
ros2 pkg prefix robot_description
```

Relancer depuis un terminal où le workspace est sourcé :

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/diff_robot_ws/install/setup.bash
ros2 launch robot_description gazebo.launch.py
```

### Le robot ne spawn pas

Vérifier le topic de description :

```bash
ros2 topic echo /robot_description --once
```

Puis les logs de `ros_gz_sim create`, `robot_state_publisher` et Gazebo.

### Les contrôleurs ne démarrent pas

```bash
ros2 node list
ros2 control list_controllers
ros2 service list | grep controller_manager
```

Vérifier que le fichier YAML utilisé correspond au mode :

```text
simulation : bumperbot_controllers.yaml
réel       : bumperbot_controllers_real.yaml
```

### Le robot réel ne répond pas

Vérifier :

```bash
ls -l /dev/ttyUSB0
groups
cat /dev/ttyUSB0
```

Causes fréquentes :

- mauvais port ;
- utilisateur absent du groupe `dialout` ;
- port occupé par Arduino IDE ;
- firmware incorrect ;
- masse non commune ;
- alimentation moteur absente ;
- mauvais ordre droite/gauche ;
- Arduino encore en phase de redémarrage.

### Le robot avance dans le mauvais sens

Le sens dépend du câblage moteur, de l'encodeur et de la variante firmware. Vérifier :

- la convention `p/n` ;
- le branchement des phases A/B ;
- les broches IN1/IN2 et IN3/IN4 ;
- le firmware `robot_control.ino` ou `robot_control_inverted.ino` ;
- l'ordre `wheel_right_joint` puis `wheel_left_joint`.

### L'odométrie dérive ou est incohérente

Mesurer et corriger :

- le rayon réel des roues ;
- la séparation réelle entre les roues ;
- la résolution encodeur ;
- le signe de chaque roue ;
- la fréquence de lecture ;
- les covariances du contrôleur.

### `/cmd_vel` ne commande rien

Identifier le topic exact :

```bash
ros2 topic list | grep cmd_vel
```

Dans le mode Gazebo complet, utiliser :

```text
/diff_drive_controller/cmd_vel_unstamped
```

Dans le contrôleur personnalisé, utiliser :

```text
/cmd_vel
```

### `use_sim_time` pose problème

En simulation, `/clock` doit être disponible :

```bash
ros2 topic echo /clock
```

Sur le robot réel, ne pas activer `use_sim_time` sans source `/clock`. Le launch `real_robot.launch.py` utilise l'horloge système.

## Validation et tests

### Build et tests ROS 2

```bash
cd ~/diff_robot_ws
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

### Vérifications de base

```bash
ros2 pkg list | grep -E 'bumperbot|controller|robot_description|robot_msgs'
ros2 node list
ros2 topic list
ros2 service list
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

### Test progressif du robot réel

1. tester l'Arduino seul ;
2. vérifier le port série à 115200 bauds ;
3. tester les moteurs roue levée ;
4. vérifier les directions et les encodeurs ;
5. lancer `ros2_control` sans charge ;
6. envoyer une commande très faible ;
7. vérifier l'arrêt après expiration du timeout ;
8. tester la translation ;
9. tester la rotation ;
10. seulement ensuite poser le robot au sol.

### Enregistrer les données

```bash
ros2 bag record \
  /diff_drive_controller/cmd_vel_unstamped \
  /diff_drive_controller/odom \
  /joint_states \
  /tf \
  /tf_static \
  /imu/out
```

Le topic `/imu/out` peut être absent si le driver MPU6050 n'est pas lancé.

## Limites connues

- Le workspace contient plusieurs configurations historiques et pédagogiques ; utilisez les launch files recommandés dans ce README.
- `bumperbot_firmware/launch/hardware_interface.launch.py` référence des packages de noms différents et n'est pas le chemin recommandé pour le robot réel.
- Le launch `controller/real_robot.launch.py` est la configuration de référence pour le robot réel.
- Les fichiers `build/`, `install/` et `log/` sont des artefacts générés.
- Le protocole série est ASCII, sans checksum ni numéro de séquence.
- L'interface matérielle ne possède pas de watchdog logiciel dédié côté Arduino.
- La position des roues est reconstruite par intégration de la vitesse reçue.
- Les compteurs encodeur sont remis à zéro à chaque fenêtre de mesure firmware.
- Les paramètres `385.0`, les rayons, les séparations et les gains PID doivent être calibrés sur le matériel réel.
- Les covariances IMU ne sont pas configurées.
- Le driver MPU6050 utilise des facteurs de conversion à valider selon la plage configurée.
- Le contrôleur personnalisé et `diff_drive_controller` utilisent des topics et des conventions distincts.
- Certaines descriptions de package contiennent encore des valeurs génériques à compléter avant une diffusion production.

### Améliorations recommandées

1. unifier les paramètres simulation/réel dans un fichier de configuration central ;
2. remplacer le protocole série par des trames validées avec checksum ;
3. ajouter un watchdog matériel et un arrêt de sécurité ;
4. publier des diagnostics ROS 2 pour le port série et les encodeurs ;
5. rendre le port série configurable par argument de launch ;
6. synchroniser les dimensions URDF et celles des contrôleurs ;
7. corriger et tester les facteurs de conversion MPU6050 ;
8. ajouter des tests d'intégration avec port série simulé ;
9. documenter les broches exactes du driver moteur et de l'Arduino utilisé ;
10. séparer les exemples pédagogiques du chemin de déploiement réel.

## Sécurité

- Ne testez jamais le robot réel sans arrêt d'urgence ou coupure de puissance.
- Commencez toujours avec les roues motrices soulevées.
- Utilisez une alimentation adaptée au courant de démarrage des moteurs.
- Ne branchez pas les moteurs directement sur les broches Arduino.
- Vérifiez les masses communes et les niveaux logiques.
- Limitez les vitesses avant le premier essai au sol.
- Surveillez la température du driver, des moteurs et du câblage.
- Coupez la puissance avant toute modification matérielle.
- Ne considérez pas le timeout ROS 2 comme une protection électrique suffisante.
- Vérifiez le sens de rotation des deux roues avant d'activer l'odométrie.

## Licence et contribution

Le fichier `LICENSE` à la racine du dépôt constitue la référence légale du projet. Vérifiez également les licences des bibliothèques Arduino, ROS 2, Gazebo, LibSerial et des composants réutilisés.

Pour contribuer :

1. créer une branche dédiée ;
2. modifier uniquement les fichiers nécessaires ;
3. compiler avec `colcon build --symlink-install` ;
4. exécuter `colcon test` ;
5. documenter toute modification du protocole série, des dimensions ou des frames ;
6. ouvrir une pull request avec les résultats de validation.

## Auteur et dépôt

- **Mainteneur :** Lacina Sidibe
- **Dépôt :** [lacinasidibe114-sudo/Diff_robot_real](https://github.com/lacinasidibe114-sudo/Diff_robot_real)
