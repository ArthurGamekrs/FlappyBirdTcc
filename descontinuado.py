import pygame
import os
import random
import neat


ai_jogando = True # Quando False, o usuário que joga
geracao = 0

tela_largura = 500
tela_altura = 800

imagem_cano = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
imagem_chao = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
imagem_background = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
imagens_passaro = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init() 
fonte_pontos = pygame.font.SysFont('arial', 40)

# Criar classes para os canos/pássaros/chão



# Atributos: pular, passar dos objetos, posição no eixo x e y etc.
class Passaro:
    IMGS = imagens_passaro
    # Animações da rotação
    rotacao_maxima = 25
    velocidade_rotacao = 20
    tempo_animacao = 5

    # Atributos
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0 # Tempo da animação de quando o pássaro pula
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0] # primeira imagem do pássaro

    # Função de pular

    def pular(self):
        self.velocidade = -10.5 #Eixo Y para cima: negativo
        self.tempo = 0 # Utilizar a função do deslocamento
        self.altura = self.y

    # Função de mover

    def mover(self):
        #calcular o deslocamento
        self.tempo += 1
        deslocando = self.velocidade * self.tempo + 1.5 * (self.tempo**2) #fórmula do sorvetão
    
        #restringir o deslocamento
        if deslocamento >= 16: #16 pixels
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2 #Dando um ganho extra para o pulo
        
        self.y += deslocamento

        #angulo do pássaro (para animação)
        if deslocamento < 0 or self.y < (self.altura + 50):#verificar na animação
             if self.angulo < self.rotacao_maxima:
                 self.angulo = self.rotacao_maxima
        else:
            if self.angulo > -90:
                self.angulo -= self.velocidade_rotacao
    
    # Desenho do pássaro
    def desenhar(self, tela):
        # qual imagem será usada pelo pássaro

        self.contagem_imagem += 1

        if self.contagem_imagem < self.tempo_animacao:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.tempo_animacao*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.tempo_animacao*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.tempo_animacao*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.tempo_animacao*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0
        
        # se o passaro tiver caindo não bater a asa
        
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.tempo_animacao*2

        # desenhando a imagem

        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft) #desenhando

    def get_mask(self): #pegando a máscara do passaro, para corrigir possível bug na colisão com o cano
        return pygame.mask.from_surface(self.imagem) 



# Atributos: Posição no eixo x, velocidade, parte de baixo e de cima.
class Cano:
    distancia = 200 #pixels
    velociddade = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.cano_topo = pygame.transform.flip(imagem_cano, False, True) #False = eixo X; True = eixo Y;
        self.cano_base = imagem_cano
        self.passou = False #passou do cano
        self.definir_altura() #altura do cano aleatorio

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.cano_topo.get_height()
        self.pos_base = self.altura + self.distancia

    #movendo os canos
    def mover(self):
        self.x -= self.velociddade
    
    #desenhando o cano
    def desenhar(self, tela):        
        tela.blit(self.cano_topo, (self.x, self.pos_topo))
        tela.blit(self.cano_base, (self.x, self.pos_base))

    #colisão

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.cano_topo) 
        base_mask = pygame.mask.from_surface(self.cano_base)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo) #colisão
        base_ponto = passaro_mask.overlap(base_mask, distancia_base) #colisão
    
        #Vendo se existe colisão
        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    velocidade = 5
    largura = imagem_chao.get_width()
    imagem = imagem_chao

    #Lógica de "dois chãos" passando na tela 


    def __init__(self, y):
        self.y = y
        self.x1 = 0 
        self.x2 = self.largura
    
    def mover(self):
        self.x1 -= self.velocidade
        self.x2 -= self.velocidade

        if self.x1 + self.largura < 0:
            self.x1 = self.x2 + self.largura

        if self.x2 + self.largura < 0:
            self.x2 = self.x1 + self.largura
    
    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x1, self.y))
        tela.blit(self.imagem, (self.x2, self.y))
 

# Desenhando o jogo

def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(imagem_background, (0, 0))

    for passaro in passaros: # para a inteligência artifical
        passaro.desenhar(tela) 

    for cano in canos:
        cano.desenhar(tela)
    
    texto = fonte_pontos.render(f"PONTUAÇÃO: {pontos}", 1, (255, 255, 255)) # 1 para deixar o texto bonito
    tela.blit(texto, (tela_largura - 10 - texto.get_width(), 10)) #texto, posição

    if ai_jogando:
        texto = fonte_pontos.render(f"Geração: {geracao}", 1, (255, 255, 255))
        tela.blit(texto, (10, 10))

    chao.desenhar(tela)
    pygame.display.update()


# Executando o jogo
def main(genomas, config): # fitness function --> o quão bem o pássaro foi ---> configuração pra neat funcionar
    global geracao # Função global geração (devido ao projeto ser simples)
    geracao += 1

    if ai_jogando:
        redes = []  # Acompanha o genoma
        lista_genomas = [] # Acompanha o pássaro
        passaros = [] # Primeiro pássaro vai ser a primeira do genoma e da rede neural... etc
        for _, genoma in genomas: # Percorrendo a lista de genomas (as configs das redes) --> O _ é abrindo a lista de tuplas de genomas
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)    # Criando a rede
            redes.append(rede)
            genoma.fitness = 0 # Pontuação do pássaro (não é a pontuação do cano -> é uma "interna")
            lista_genomas.append(genoma)
            passaros.append(Passaro(230, 350)) # Criando o pássaro
    else:
       passaros = [Passaro(230, 350)]
    
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((tela_largura, tela_altura))
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30) #framerate
        
        #Interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not ai_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

        indice_cano = 0 # Primeiro cano
        if len(passaros) > 0:   # Se ainda tiver pássaros vivos
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].cano_topo.get_width()):    # Lógica de qual cano olhar
                indice_cano = 1
        else: 
            rodando: False
            break      # Acaba o jogo


        #Movendo as coisas
        for i, passaro in enumerate(passaros):
            passaro.mover()
            # Aumentar o fitness do pássaro (genoma) --> colocando a IA pra pular ou não
            lista_genomas[i].fitness += 0.1     # Pontuação pequena para a rede neural aprender
            output = redes[i].activate((passaro.y,
                                    abs(passaro.y - canos[indice_cano].altura),
                                    abs(passaro.y - canos[indice_cano].pos_base)))   # Botando a IA pra pular; ela trabalha melhor com número positivos
            # -1 e 1 --> se o output for > 0.5 então ele pula
            if output[0] > 0.5:
                passaro.pular()

        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros): #Para cada posição do pássaros + pássaros dentro da lista:
                if cano.colidir(passaro):
                    passaros.pop(i)  #Exclue
                    if ai_jogando: # "Penalizar a geração que errou"
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)

                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.cano_topo.get_width() < 0: # Tirando canos da tela
                remover_canos.append(cano)
        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
            for genoma in lista_genomas:
                genoma.fitness += 5
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros): #Caso o pássaro passe do céu ou do chão
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if ai_jogando:  # Tirando os pássaros ---> Talvez tirar pontos do genoma (verificar)
                    lista_genomas.pop(i)
                    redes.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos)

def rodar(caminho_config):
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        caminho_config
    )

    populacao = neat.Population(config)
    #Adicionando estatísticas
    populacao.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    populacao.add_reporter(stats)

    if ai_jogando:
        populacao.run(main, 50)     # O 50 é o número de geração, pode deixar sem
    else:
        main(None, None) # Sem os parâmetros da IA

if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)
