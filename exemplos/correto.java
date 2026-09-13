public class CalculadoraSimples {

    public static void main(String[] args) {

        int contador = 10;

        float taxa = 3.14;

        double media = 2.5;

        boolean ativo;

        byte nivel = 1;

        short limite = 20;

        long total = 1000;

        final int passo = 1;

        char quebra = '\n';

        String mensagem =
            "Analisador funcionando\n";

        contador += 2;

        if (
            contador >= 10
            && taxa != 0.0
        ) {

            System.out.println(
                mensagem
            );

        } else {

            contador = 0;
        }

        for (
            int indice = 0;
            indice < 3;
            indice += 1
        ) {

            continue;
        }

        while (contador > 0) {

            contador -= passo;
            break;
        }

        // Comentário ignorado

        contador = contador - 1;

        /*
         * Comentário de bloco.
         */

        return;
    }
}
