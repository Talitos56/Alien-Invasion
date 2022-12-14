import sys
from time import sleep
import pygame
from bullet import Bullet
from alien import Alien


def check_keydown_events(event, ai_settings, screen, stats,
                         sb, ship, aliens, bullets):
    """Responde a pressionamentos de tecla."""

    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship,
                    bullets, stats)
    elif event.key == pygame.K_q:
        save_high_score(stats)
        sys.exit()
    elif event.key == pygame.K_p:
        if not stats.game_active:
            start_game(ai_settings, screen, stats, sb,
                       ship, aliens, bullets)


def check_keyup_events(event, ship):
    """Responde a solturas de tecla."""

    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ai_settings, screen, stats, sb,
                 play_button, ship, aliens, bullets):
    """Responde a eventos de pressionamento de teclas e de mouse."""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score(stats)
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats,
                                 sb, ship, aliens, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb,
                              play_button, ship, aliens, bullets,
                              mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats, sb, play_button,
                      ship, aliens, bullets, mouse_x, mouse_y):
    """Inicia um novo jogo quando o jogador clicar em Play."""

    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings, screen, stats, sb,
                   ship, aliens, bullets)


def start_game(ai_settings, screen, stats, sb,
               ship, aliens, bullets):
    """Inicia ou Reinicia o jogo quando clica em play
        ou quando aperta a tecla P"""

    # Reinicia os dados estat??sticos do jogo
    stats.reset_stats()
    stats.game_active = True
    # Reinicia as imagens do painel de pontua????o
    sb.prep_images()
    # Reinicia as configura????es do jogo
    ai_settings.initialize_dynamic_settings()
    # Oculta o cursor do mouse
    pygame.mouse.set_visible(False)
    # Esvazia a lista de alien??genas e de proj??teis
    aliens.empty()
    bullets.empty()
    # Cria a nova frota e centraliza a espa??onave
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()


def update_screen(ai_settings, screen, stats, sb, ship,
                  aliens, bullets, play_button):
    """Atualiza as imagens na tela e alterna para a nova tela."""

    # Redesenha a tela a cada passagem pelo la??o
    screen.fill(ai_settings.bg_color)
    ship.blitme()
    aliens.draw(screen)
    # Redesenha todos os proj??teis atr??s da espa??onave
    # e dos alien??genas
    for bullet in bullets.sprites():
        bullet.draw_bullet()
        ship.blitme()
        aliens.draw(screen)

    # Desenha a informa????o sobre pontua????o
    sb.show_score()  # desenha antes do play

    # Desenha o bot??o Play se o jogo estiver inativo
    if not stats.game_active:
        play_button.draw_button()

    # Deixa a tela mais recente vis??vel
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb,
                   ship, aliens, bullets):
    """Atualiza a posi????o dos proj??teis e se livra dos proj??teis antigos."""

    # Atualiza as posi????es dos proj??teis
    bullets.update()
    # Livra-se dos proj??teis que desapareceram
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings, screen, stats, sb,
                                  ship, aliens, bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb,
                                  ship, aliens, bullets):
    """Responde a colis??es entre proj??teis e alien??genas."""

    # Remove qualquer proj??til e alien??gena que tenham colidido
    collisions = pygame.sprite.groupcollide(bullets, aliens,
                                            True, True)
    if collisions:  # devolve um dicion??rio
        explosion_sound()
        for aliens in collisions.values():
            # O valor associado a cada proj??til ?? uma
            # lista de alien??genas
            stats.score += ai_settings.alien_points * len(aliens)
        sb.prep_score()
        check_high_score(stats, sb)
    if len(aliens) == 0:
        start_new_level(ai_settings, screen, stats, sb,
                        ship, aliens, bullets)


def start_new_level(ai_settings, screen, stats, sb,
                    ship, aliens, bullets):
    """Inicia um novo n??vel quando a frota ?? destru??da
       aumenta a velocidade e cria a nova frota"""

    # Se a frota toda for destru??da, inicia um novo n??vel
    bullets.empty()
    ai_settings.increase_speed()
    # Aumenta o n??vel
    stats.level += 1
    sb.prep_level()
    create_fleet(ai_settings, screen, ship, aliens)


def fire_bullet(ai_settings, screen, ship, bullets, stats):
    """Dispara um proj??til se o limite ainda n??o foi alcan??ado."""

    # Cria um proj??til e o adiciona ao grupo de proj??teis
    if len(bullets) < ai_settings.bullets_allowed\
            and stats.game_active:
        new_bullet = Bullet(ai_settings, screen, ship)
        shot_sound()
        bullets.add(new_bullet)


def get_number_aliens_x(ai_settings, alien_width):
    """Determina o n??mero de alien??genas que cabem numa linha."""

    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def create_alien(ai_settings, screen, aliens, alien_number,
                 row_number):
    # Cria um alien??gena e o posiciona na linha
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Cria uma frota completa de alien??genas."""

    # Cria um alien??gena e calcula o n??mero de alien??genas em uma linha
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
                                  alien.rect.height)
    # Cria a primeira linha de alien??genas
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens,
                         alien_number, row_number)


def get_number_rows(ai_settings, ship_height, alien_height):
    """Determina o n??mero de linhas com alien??genas que cabem na tela."""

    available_space_y = (ai_settings.screen_height - (3 * alien_height)
                         - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def update_aliens(ai_settings, screen, stats, sb,
                  ship, aliens, bullets):
    """Verifica se a frota est?? em uma das bordas e ent??o
        atualiza as posi????es de todos os alien??genas da frota."""

    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    # Verifica se houve colis??es entre alien??genas e a espa??onave
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, sb,
                 ship, aliens, bullets)
    # Verifica se h?? algum alien??gena que atingiu a parte inferior da tela
    check_aliens_bottom(ai_settings, stats, sb, screen,
                        ship, aliens, bullets)


def check_fleet_edges(ai_settings, aliens):
    """Responde apropriadamente se algum alien??gena alcan??ou uma borda."""

    for alien in aliens.sprites():
        if alien.check_edges():  # se retornar True no m??dulo alien
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Faz toda a frota descer e muda a sua dire????o."""

    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, screen, sb,
             ship, aliens, bullets):
    """Responde ao fato de a espa??onave ter sido atingida por um
        alien??gena."""

    if stats.ships_left > 0:
        # Decrementa ships_left
        stats.ships_left -= 1
        # Atualiza o painel de pontua????es
        sb.prep_ships()
        # Esvazia a lista de alien??genas e de proj??teis
        aliens.empty()
        bullets.empty()
        # Cria a nova frota e centraliza a espa??onave
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
        # Faz uma pausa
        sleep(0.5)
    else:
        stop_music()
        dead_end_sound()
        stats.game_active = False
        pygame.mouse.set_visible(True)
        sleep(1)
        play_music()


def check_aliens_bottom(ai_settings, stats, sb, screen,
                        ship, aliens, bullets):
    """Verifica se algum alien??gena alcan??ou a parte
        inferior da tela."""

    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Trata esse caso do mesmo modo que quando a
            # espa??onave ?? atingida
            ship_hit(ai_settings, stats, screen, sb,
                     ship, aliens, bullets)
            break


def check_high_score(stats, sb):
    """Verifica se h?? uma nova pontua????o m??xima."""

    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def save_high_score(stats):
    """Salva a pontua????o m??xima num arquivo
       quando fechamos o jogo"""

    filename = 'high_score.txt'
    with open(filename, 'w') as file_object:  # o w escreve
        file_object.write(str(stats.high_score))


def play_music():
    """Toca a m??sica de fundo quando abrir o jogo"""

    pygame.mixer.music.load('sounds/arcade-music.wav')
    pygame.mixer.music.play(-1)


def stop_music():
    """Para de tocar a m??sica de fundo"""

    pygame.mixer.music.stop()


def explosion_sound():
    """Toca o som de explos??o quando atinge um alien"""

    sound_effect = pygame.mixer.Sound('sounds/explode.wav')
    sound_effect.play()


def dead_end_sound():
    """Toca quando o jogador perde"""

    sound1_effect = pygame.mixer.Sound('sounds/dead-end.wav')
    sound1_effect.play()


def shot_sound():
    """Som de tiro quando atira"""

    sound2_effect = pygame.mixer.Sound('sounds/shot.wav')
    sound2_effect.play()
